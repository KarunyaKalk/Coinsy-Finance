def test_job_application_tracker_crud(client, sample_user):
    # 1. Create Job Application
    create_payload = {
        "company_name": "Stripe",
        "job_title": "Senior Backend Engineer",
        "job_description": "We are seeking a Backend Engineer with experience in Python microservices, REST APIs, PostgreSQL, and high availability system design.",
        "status": "Applied",
        "location": "Remote / San Francisco",
        "salary_range": "$180k - $220k"
    }
    create_res = client.post(f"/api/v1/jobs?user_id={sample_user.id}", json=create_payload)
    assert create_res.status_code == 201
    job_data = create_res.json()

    assert job_data["company_name"] == "Stripe"
    assert job_data["status"] == "Applied"
    assert job_data["has_prep_pack"] is False

    job_id = job_data["id"]

    # 2. Update status to 'Interview'
    update_payload = {"status": "Interview"}
    update_res = client.put(f"/api/v1/jobs/{job_id}?user_id={sample_user.id}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "Interview"

    # 3. List jobs
    list_res = client.get(f"/api/v1/jobs?user_id={sample_user.id}")
    assert list_res.status_code == 200
    jobs = list_res.json()
    assert len(jobs) == 1
    assert jobs[0]["company_name"] == "Stripe"


def test_generate_and_fetch_interview_prep_pack(client, sample_user):
    # Create Job in 'Interview' status
    job_payload = {
        "company_name": "Fintech Corp",
        "job_title": "Staff Python Engineer",
        "job_description": "Build high frequency payments pipeline using FastAPI, SQL, Redis, and LLM integrations.",
        "status": "Interview"
    }
    job_res = client.post(f"/api/v1/jobs?user_id={sample_user.id}", json=job_payload)
    job_id = job_res.json()["id"]

    # Save custom user resume first
    resume_payload = {
        "title": "Main Resume 2026",
        "content": "Experienced Python Engineer. Built background queue architectures, automated unit test pipelines with pytest, and integrated Claude LLM AI APIs."
    }
    client.post(f"/api/v1/interview-prep/resume/me?user_id={sample_user.id}", json=resume_payload)

    # Generate Prep Pack
    gen_res = client.post(f"/api/v1/interview-prep/generate/{job_id}?user_id={sample_user.id}")
    assert gen_res.status_code == 200
    pack_data = gen_res.json()

    assert pack_data["job_id"] == job_id
    assert pack_data["total_count"] > 0
    assert len(pack_data["company_context"]) > 0

    items = pack_data["items"]
    types = [i["item_type"] for i in items]
    assert "technical" in types or "star_answer" in types or "company_notes" in types

    # Check STAR format structure for star_answer item
    star_items = [i for i in items if i["item_type"] == "star_answer"]
    if star_items:
        s_item = star_items[0]
        assert s_item["star_situation"] is not None
        assert s_item["star_action"] is not None


def test_checklist_item_ticking_and_custom_notes(client, sample_user):
    # Create job & generate prep pack
    job_res = client.post(f"/api/v1/jobs?user_id={sample_user.id}", json={
        "company_name": "Acme Inc",
        "job_title": "Full Stack Dev",
        "job_description": "React, Python, Postgres stack.",
        "status": "Interview"
    })
    job_id = job_res.json()["id"]

    gen_res = client.post(f"/api/v1/interview-prep/generate/{job_id}?user_id={sample_user.id}")
    items = gen_res.json()["items"]
    target_item_id = items[0]["id"]

    # Patch item: tick checkbox + add custom notes
    patch_payload = {
        "is_completed": True,
        "user_notes": "Mention my work on microservices architecture during 2025."
    }
    patch_res = client.patch(
        f"/api/v1/interview-prep/items/{target_item_id}?user_id={sample_user.id}",
        json=patch_payload
    )
    assert patch_res.status_code == 200
    patched_data = patch_res.json()

    assert patched_data["is_completed"] is True
    assert patched_data["user_notes"] == "Mention my work on microservices architecture during 2025."

    # Verify updated prep pack completion counter
    pack_res = client.get(f"/api/v1/interview-prep/{job_id}?user_id={sample_user.id}")
    assert pack_res.status_code == 200
    assert pack_res.json()["completed_count"] == 1
