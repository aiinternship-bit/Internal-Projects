#!/bin/bash
# Verification script to ensure port fixes are in place

echo "🔍 Verifying port configuration fixes..."
echo ""

# Check app.py
echo "1. Checking AI-Interns/app.py for PORT environment variable..."
if grep -q "os.environ.get('PORT'" AI-Interns/app.py; then
    echo "   ✅ app.py has PORT environment variable support"
else
    echo "   ❌ app.py is missing PORT environment variable support"
    echo "   Run these commands to fix:"
    echo "   sed -i \"s/app.run(debug=True, host='0.0.0.0', port=5001)/port = int(os.environ.get('PORT', 5001))\\n    app.run(debug=True, host='0.0.0.0', port=port)/\" AI-Interns/app.py"
fi
echo ""

# Check Dockerfile
echo "2. Checking Dockerfile for PORT=8080..."
if grep -q "ENV PORT=8080" Dockerfile; then
    echo "   ✅ Dockerfile has PORT=8080"
else
    echo "   ❌ Dockerfile is missing PORT=8080"
fi

if grep -q "EXPOSE 8080" Dockerfile; then
    echo "   ✅ Dockerfile exposes port 8080"
else
    echo "   ❌ Dockerfile doesn't expose port 8080"
fi
echo ""

# Show what will be in the image
echo "3. Current configuration:"
echo "   - Dockerfile EXPOSE: $(grep EXPOSE Dockerfile | head -1)"
echo "   - Dockerfile ENV PORT: $(grep 'ENV PORT' Dockerfile)"
echo "   - app.py port config: $(grep -A 1 'PORT' AI-Interns/app.py | grep -v '#' | head -2)"
echo ""

echo "✅ Verification complete!"
echo ""
echo "Next steps:"
echo "1. If any checks failed, fix them first"
echo "2. Then rebuild: gcloud builds submit --config cloudbuild.yaml ."
echo "3. Then deploy: gcloud run deploy ai-interns --image gcr.io/\$(gcloud config get-value project)/ai-interns:latest ..."
