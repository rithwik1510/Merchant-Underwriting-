$ErrorActionPreference = "Stop"

param(
    [string]$MerchantId = "m_freshbasket",
    [string]$RecipientPhone = "",
    [string]$MessageType = "combined_offer",
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

if (-not $RecipientPhone) {
    throw "Pass -RecipientPhone in Twilio WhatsApp format, for example whatsapp:+91XXXXXXXXXX"
}

$runResponse = Invoke-RestMethod -Method POST -Uri "$BaseUrl/api/underwriting/run/$MerchantId"
$runId = $runResponse.run_id

$draftResponse = Invoke-RestMethod `
    -Method POST `
    -Uri "$BaseUrl/api/underwriting/runs/$runId/whatsapp-draft" `
    -ContentType "application/json" `
    -Body (@{ message_type = $MessageType } | ConvertTo-Json)

$sendResponse = Invoke-RestMethod `
    -Method POST `
    -Uri "$BaseUrl/api/underwriting/runs/$runId/send-whatsapp" `
    -ContentType "application/json" `
    -Body (@{ recipient_phone = $RecipientPhone; message_type = $MessageType } | ConvertTo-Json)

[PSCustomObject]@{
    run_id = $runId
    draft_provider = $draftResponse.provider_name
    draft_status = $draftResponse.status
    draft_message = $draftResponse.output_payload_json.message_body
    delivery_status = $sendResponse.delivery_status
    twilio_message_sid = $sendResponse.twilio_message_sid
    failure_reason = $sendResponse.failure_reason
} | Format-List
