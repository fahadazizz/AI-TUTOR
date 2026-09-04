#!/bin/bash
# AI Tutor — Live API End-to-End Test (Rule 7)

# Stop on first error
set -e

# Change to the backend directory
cd "$(dirname "$0")/.."

echo "=========================================="
echo "    AI Tutor Live API Test (Rule 7)       "
echo "=========================================="

echo "[1/4] Starting Uvicorn server in background..."
export APP_ENV=development
./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001 &
UVICORN_PID=$!

# Ensure we kill the server on exit
trap "echo 'Cleaning up server (PID: $UVICORN_PID)...'; kill $UVICORN_PID 2>/dev/null || true" EXIT

# Wait for server to start
echo "Waiting for server to be healthy..."
sleep 5
for i in {1..10}; do
    if curl -s http://127.0.0.1:8001/health | grep '"status":"ok"' > /dev/null; then
        echo "Server is healthy!"
        break
    fi
    sleep 1
    if [ "$i" -eq 10 ]; then
        echo "Server failed to start in time!"
        exit 1
    fi
done

echo ""
echo "[2/4] Registering a new student..."
REG_RESP=$(curl -s -X POST "http://127.0.0.1:8001/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Student", "phone": "1234567890", "class_level": 10, "board": "punjab", "group_type": "science", "preferred_language": "ur"}')

STUDENT_ID=$(echo $REG_RESP | grep -o '"student_id":"[^"]*' | cut -d'"' -f4)
if [ -z "$STUDENT_ID" ]; then
    echo "Failed to register student. Response: $REG_RESP"
    exit 1
fi
echo "Registered Student ID: $STUDENT_ID"


echo ""
echo "[3/4] Starting a new tutoring session..."
SESS_RESP=$(curl -s -X POST "http://127.0.0.1:8001/api/auth/start-session" \
     -H "Content-Type: application/json" \
     -d "{\"student_id\": \"$STUDENT_ID\", \"subject_key\": \"mathematics\"}")

SESSION_ID=$(echo $SESS_RESP | grep -o '"session_id":"[^"]*' | cut -d'"' -f4)
if [ -z "$SESSION_ID" ]; then
    echo "Failed to start session. Response: $SESS_RESP"
    exit 1
fi
echo "Started Session ID: $SESSION_ID"


echo ""
echo "[4/4] Interacting with the /api/chat endpoint..."
echo "Sending: 'assalam o alaikum'"
CHAT_RESP=$(curl -s -X POST "http://127.0.0.1:8001/api/chat" \
     -H "Content-Type: application/json" \
     -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"assalam o alaikum\"}")

# The response should have action_taken and response
ACTION_TAKEN=$(echo $CHAT_RESP | grep -o '"action_taken":"[^"]*' | cut -d'"' -f4)
TUTOR_RESPONSE=$(echo $CHAT_RESP | grep -o '"response":"[^"]*' | cut -d'"' -f4)

echo ""
echo "--- Tutor Response ---"
echo "Action taken: $ACTION_TAKEN"
echo "Tutor: $TUTOR_RESPONSE"
echo "----------------------"

if [ -z "$ACTION_TAKEN" ]; then
    echo "Chat request failed. Full response: $CHAT_RESP"
    exit 1
fi

echo ""
echo "=========================================="
echo "    Live API Test Completed Successfully! "
echo "=========================================="
