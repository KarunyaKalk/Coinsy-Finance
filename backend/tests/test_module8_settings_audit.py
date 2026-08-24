def test_user_settings_crud(client, sample_user):
    # 1. Fetch default settings
    get_res = client.get(f"/api/v1/settings?user_id={sample_user.id}")
    assert get_res.status_code == 200
    data = get_res.json()

    assert data["scan_frequency"] == "6h"
    assert data["ats_threshold"] == 75.0
    assert data["daily_app_cap"] == 15
    assert data["active_platforms"]["linkedin"] is True

    # 2. Update settings & platform toggles
    update_payload = {
        "scan_frequency": "12h",
        "ats_threshold": 80.0,
        "daily_app_cap": 20,
        "daily_email_cap": 8,
        "active_platforms": {
            "linkedin": True,
            "indeed": True,
            "glassdoor": True,
            "wellfound": True,
            "ziprecruiter": False
        },
        "telegram_webhook_url": "https://api.telegram.org/bot12345/sendMessage",
        "email_notification_address": "user@example.com"
    }

    put_res = client.put(f"/api/v1/settings?user_id={sample_user.id}", json=update_payload)
    assert put_res.status_code == 200
    updated_data = put_res.json()

    assert updated_data["scan_frequency"] == "12h"
    assert updated_data["ats_threshold"] == 80.0
    assert updated_data["daily_app_cap"] == 20
    assert updated_data["active_platforms"]["glassdoor"] is True
    assert updated_data["telegram_webhook_url"] == "https://api.telegram.org/bot12345/sendMessage"


def test_audit_log_feed_and_filtering(client, sample_user):
    # Fetch initial audit logs
    res0 = client.get(f"/api/v1/audit?user_id={sample_user.id}")
    assert res0.status_code == 200
    logs = res0.json()

    # Trigger block alert simulation
    block_req = {
        "platform": "LinkedIn",
        "error_message": "Automated login challenged by CAPTCHA"
    }
    block_res = client.post(f"/api/v1/audit/trigger-block-alert?user_id={sample_user.id}", json=block_req)
    assert block_res.status_code == 200
    assert block_res.json()["status"] == "blocked"

    # Filter by action_type=captcha_blocked
    filter_res = client.get(f"/api/v1/audit?user_id={sample_user.id}&action_type=captcha_blocked")
    assert filter_res.status_code == 200
    filtered_logs = filter_res.json()
    assert len(filtered_logs) >= 1
    assert filtered_logs[0]["status"] == "blocked"
    assert filtered_logs[0]["platform"] == "LinkedIn"

    # Verify Coinsy Mascot Widget captured the block notification
    widget_res = client.get(f"/api/v1/budgets/coinsy-widget?user_id={sample_user.id}")
    assert widget_res.status_code == 200
    assert widget_res.json()["mascot_mood"] == "concerned"
