# 🔐 GFPGAN Free API - Authentication Guide

## Free API Key

**API Key Name:** `freeApiluminascalem`

**Secret Key:** `freeApiluminascalem!+|I1,R1u31C_V`

---

## How to Use

### 1. JavaScript / Web Frontend

```javascript
// Using fetch API
const apiKey = "freeApiluminascalem!+|I1,R1u31C_V";
const imageFile = document.getElementById('imageInput').files[0];

const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('http://localhost:8000/enhance?scale=2', {
    method: 'POST',
    headers: {
        'X-API-Key': apiKey
    },
    body: formData
});

if (response.ok) {
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    
    // Show enhanced image
    document.getElementById('result').src = url;
    
    // Get quota info
    const quotaUsed = response.headers.get('X-Quota-Used');
    const quotaLimit = response.headers.get('X-Quota-Limit');
    const authenticated = response.headers.get('X-Authenticated');
    
    console.log(`Quota: ${quotaUsed}/${quotaLimit}`);
    console.log(`Authenticated: ${authenticated}`);
} else {
    console.error(`Error: ${response.status}`);
    const error = await response.json();
    console.error(error.detail);
}
```

### 2. React Component

```jsx
import React, { useState } from 'react';

const GFPGANUpscaler = () => {
    const API_KEY = "freeApiluminascalem!+|I1,R1u31C_V";
    const API_URL = "http://localhost:8000";
    
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [quota, setQuota] = useState(null);
    
    const handleUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        setLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${API_URL}/enhance?scale=2`, {
                method: 'POST',
                headers: {
                    'X-API-Key': API_KEY
                },
                body: formData
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                setResult(url);
                setQuota({
                    used: response.headers.get('X-Quota-Used'),
                    limit: response.headers.get('X-Quota-Limit'),
                    reset: response.headers.get('X-Quota-Reset'),
                    authenticated: response.headers.get('X-Authenticated')
                });
            } else {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div>
            <h1>GFPGAN Face Enhancement</h1>
            
            <input 
                type="file" 
                accept="image/*"
                onChange={handleUpload}
                disabled={loading}
            />
            
            {loading && <p>Processing...</p>}
            
            {result && <img src={result} alt="Enhanced" />}
            
            {quota && (
                <div>
                    <p>Quota: {quota.used}/{quota.limit}</p>
                    <p>Authenticated: {quota.authenticated}</p>
                    <p>Reset: {quota.reset}</p>
                </div>
            )}
        </div>
    );
};

export default GFPGANUpscaler;
```

### 3. Python

```python
import requests
from pathlib import Path

API_KEY = "freeApiluminascalem!+|I1,R1u31C_V"
API_URL = "http://localhost:8000"

def enhance_image(image_path, scale=2):
    """Enhance image using GFPGAN API"""
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        headers = {'X-API-Key': API_KEY}
        
        response = requests.post(
            f"{API_URL}/enhance",
            params={'scale': scale},
            files=files,
            headers=headers,
            timeout=60
        )
    
    if response.status_code == 200:
        # Save result
        with open('enhanced.png', 'wb') as out:
            out.write(response.content)
        
        # Print quota info
        print(f"✅ Enhancement successful!")
        print(f"Quota used: {response.headers.get('X-Quota-Used')}/{response.headers.get('X-Quota-Limit')}")
        print(f"Authenticated: {response.headers.get('X-Authenticated')}")
        return True
    
    elif response.status_code == 401:
        print("❌ Invalid API key")
        return False
    
    elif response.status_code == 429:
        print(f"❌ Quota exceeded: {response.json()['detail']}")
        return False
    
    else:
        print(f"❌ Error {response.status_code}: {response.json()['detail']}")
        return False

# Usage
enhance_image('face.jpg', scale=2)
```

### 4. cURL

```bash
# Basic usage
curl -X POST "http://localhost:8000/enhance?scale=2" \
  -H "X-API-Key: freeApiluminascalem!+|I1,R1u31C_V" \
  -F "file=@face.jpg" \
  --output enhanced.png

# With quota info
curl -i -X POST "http://localhost:8000/enhance?scale=4" \
  -H "X-API-Key: freeApiluminascalem!+|I1,R1u31C_V" \
  -F "file=@face.jpg" \
  --output enhanced.png

# Check response headers
curl -X POST "http://localhost:8000/enhance?scale=2" \
  -H "X-API-Key: freeApiluminascalem!+|I1,R1u31C_V" \
  -F "file=@face.jpg" \
  -i | grep -E "X-Quota|X-Authenticated"
```

### 5. Node.js / Express

```javascript
const fetch = require('node-fetch');
const FormData = require('form-data');
const fs = require('fs');

const API_KEY = "freeApiluminascalem!+|I1,R1u31C_V";
const API_URL = "http://localhost:8000";

async function enhanceImage(imagePath) {
    try {
        const form = new FormData();
        form.append('file', fs.createReadStream(imagePath));
        
        const response = await fetch(`${API_URL}/enhance?scale=2`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY,
                ...form.getHeaders()
            },
            body: form
        });
        
        if (response.ok) {
            const buffer = await response.buffer();
            fs.writeFileSync('enhanced.png', buffer);
            
            console.log('✅ Enhancement complete');
            console.log(`Quota: ${response.headers.get('x-quota-used')}/${response.headers.get('x-quota-limit')}`);
            console.log(`Authenticated: ${response.headers.get('x-authenticated')}`);
            
            return true;
        } else {
            const error = await response.json();
            console.error(`❌ Error: ${error.detail}`);
            return false;
        }
    } catch (error) {
        console.error(`Error: ${error.message}`);
        return false;
    }
}

// Usage
enhanceImage('face.jpg');
```

### 6. PHP

```php
<?php

$apiKey = "freeApiluminascalem!+|I1,R1u31C_V";
$apiUrl = "http://localhost:8000/enhance";

function enhanceImage($imagePath, $scale = 2) {
    global $apiKey, $apiUrl;
    
    // Prepare multipart form data
    $cFile = new CURLFile($imagePath);
    $post = array("file" => $cFile);
    
    // Initialize cURL
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "$apiUrl?scale=$scale");
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        "X-API-Key: $apiKey"
    ));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 60);
    
    // Execute request
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $headers = curl_getinfo($ch);
    
    curl_close($ch);
    
    if ($httpCode === 200) {
        // Save result
        file_put_contents('enhanced.png', $response);
        
        echo "✅ Enhancement complete\n";
        echo "Quota: " . $headers['x-quota-used'] . "/" . $headers['x-quota-limit'] . "\n";
        echo "Authenticated: " . $headers['x-authenticated'] . "\n";
        
        return true;
    } else {
        echo "❌ Error $httpCode\n";
        return false;
    }
}

// Usage
enhanceImage('face.jpg', 2);
```

---

## Response Headers

Every successful response includes quota information:

```
X-Quota-Used: 42           # Requests used today
X-Quota-Limit: 10000       # Daily limit
X-Quota-Reset: 2024-02-05T23:59:59Z  # Reset time
X-Authenticated: true      # Authentication status
```

---

## Error Handling

### Missing API Key
```
401 Unauthorized
{
  "detail": "Missing X-API-Key header"
}
```

### Invalid API Key
```
401 Unauthorized
{
  "detail": "Invalid API key"
}
```

### Quota Exceeded
```
429 Too Many Requests
{
  "detail": "Daily quota exceeded (10001/10000). Resets at 2024-02-05T23:59:59Z"
}

Headers:
X-Quota-Used: 10001
X-Quota-Limit: 10000
X-Quota-Reset: 2024-02-05T23:59:59Z
Retry-After: 86400
```

### Invalid File
```
400 Bad Request
{
  "detail": "Invalid image format - supported formats: JPG, PNG, WebP, etc."
}
```

---

## Testing Your API Key

### Check if API is running
```bash
curl http://localhost:8000/health
```

### Check API stats
```bash
curl http://localhost:8000/stats
```

### Test with your API key
```bash
curl -X POST "http://localhost:8000/enhance?scale=2" \
  -H "X-API-Key: freeApiluminascalem!+|I1,R1u31C_V" \
  -F "file=@test.jpg" \
  -i
```

---

## Security Tips

✅ **Store API key in environment variables** (not in code)
```javascript
const API_KEY = process.env.GFPGAN_API_KEY;
```

✅ **Use HTTPS in production**
```javascript
// Development
const API_URL = "http://localhost:8000";

// Production
const API_URL = "https://api.yourdomain.com";
```

✅ **Never expose key in client-side code**
```javascript
// ❌ BAD - Key visible in browser
const API_KEY = "freeApiluminascalem!+|I1,R1u31C_V";

// ✅ GOOD - Use backend proxy
fetch('/api/enhance', {
    method: 'POST',
    body: formData
});
```

✅ **Implement backend proxy** (recommended)
```javascript
// Backend route (Node.js/Express)
app.post('/api/enhance', async (req, res) => {
    const formData = new FormData();
    formData.append('file', req.file.buffer);
    
    const response = await fetch('http://localhost:8000/enhance', {
        method: 'POST',
        headers: {
            'X-API-Key': process.env.GFPGAN_API_KEY
        },
        body: formData
    });
    
    const blob = await response.blob();
    res.send(blob);
});
```

---

## API Limits

- **Daily limit:** 10,000 requests per API key
- **File size:** Max 50MB
- **Supported formats:** JPG, PNG, WebP, TIFF
- **Scale options:** 2x or 4x
- **Timeout:** 60 seconds per request
- **Quota reset:** UTC midnight (00:00 UTC)

---

## Example Implementation

### Full HTML + JavaScript Website

```html
<!DOCTYPE html>
<html>
<head>
    <title>GFPGAN Face Enhancer</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; }
        .container { border: 1px solid #ccc; padding: 20px; }
        input[type="file"] { margin: 10px 0; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; }
        img { max-width: 100%; margin: 10px 0; }
        .quota { padding: 10px; background: #f0f0f0; margin: 10px 0; }
        .loading { color: #666; }
        .error { color: #d32f2f; }
        .success { color: #388e3c; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 GFPGAN Face Enhancer</h1>
        
        <div>
            <label>Upload Image:</label>
            <input type="file" id="imageInput" accept="image/*">
        </div>
        
        <div>
            <label>Scale:</label>
            <select id="scaleInput">
                <option value="2">2x Upscale</option>
                <option value="4">4x Upscale</option>
            </select>
        </div>
        
        <button onclick="enhanceImage()">✨ Enhance</button>
        
        <div id="message"></div>
        
        <div id="result" class="result" style="display:none;">
            <h3>Enhanced Image</h3>
            <img id="resultImage" alt="Enhanced">
            <div id="quotaInfo" class="quota"></div>
        </div>
    </div>
    
    <script>
        const API_KEY = "freeApiluminascalem!+|I1,R1u31C_V";
        const API_URL = "http://localhost:8000";
        
        async function enhanceImage() {
            const file = document.getElementById('imageInput').files[0];
            const scale = document.getElementById('scaleInput').value;
            const messageDiv = document.getElementById('message');
            const resultDiv = document.getElementById('result');
            
            if (!file) {
                messageDiv.className = 'error';
                messageDiv.textContent = '❌ Please select an image';
                return;
            }
            
            messageDiv.className = 'loading';
            messageDiv.textContent = '⏳ Processing... this may take a few seconds';
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch(`${API_URL}/enhance?scale=${scale}`, {
                    method: 'POST',
                    headers: { 'X-API-Key': API_KEY },
                    body: formData
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    
                    document.getElementById('resultImage').src = url;
                    
                    const quotaUsed = response.headers.get('X-Quota-Used');
                    const quotaLimit = response.headers.get('X-Quota-Limit');
                    const reset = response.headers.get('X-Quota-Reset');
                    
                    document.getElementById('quotaInfo').innerHTML = `
                        <strong>Quota:</strong> ${quotaUsed}/${quotaLimit}<br>
                        <strong>Reset:</strong> ${reset}
                    `;
                    
                    resultDiv.style.display = 'block';
                    messageDiv.className = 'success';
                    messageDiv.textContent = '✅ Enhancement complete!';
                } else {
                    const error = await response.json();
                    messageDiv.className = 'error';
                    messageDiv.textContent = `❌ Error: ${error.detail}`;
                }
            } catch (error) {
                messageDiv.className = 'error';
                messageDiv.textContent = `❌ Error: ${error.message}`;
            }
        }
    </script>
</body>
</html>
```

---

**Ready to integrate!** 🚀
