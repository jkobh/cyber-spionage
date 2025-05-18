// Basic client-side functionality for WhistleDrop

document.addEventListener('DOMContentLoaded', function() {
    // Show file name when selected
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : 'No file selected';
            const fileLabel = document.querySelector('.file-name');
            if (!fileLabel) {
                const label = document.createElement('span');
                label.className = 'file-name';
                label.textContent = fileName;
                this.parentNode.appendChild(label);
            } else {
                fileLabel.textContent = fileName;
            }
        });
    }

    // Success page auto-close warning
    const successMessage = document.querySelector('.success-message');
    if (successMessage) {
        // Add a countdown timer for security
        let timeLeft = 60;
        const timerElement = document.createElement('p');
        timerElement.className = 'timer';
        timerElement.textContent = `For security, this page will automatically reload in ${timeLeft} seconds.`;
        successMessage.appendChild(timerElement);
        
        const intervalId = setInterval(function() {
            timeLeft--;
            timerElement.textContent = `For security, this page will automatically reload in ${timeLeft} seconds.`;
            
            if (timeLeft <= 0) {
                clearInterval(intervalId);
                window.location.href = '/';
            }
        }, 1000);
    }

    // Onion address copy button
    const onionAddress = document.querySelector('.onion-address');
    if (onionAddress) {
        const text = onionAddress.textContent;
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.textContent = 'Copy';
        copyBtn.style.marginLeft = '10px';
        copyBtn.style.padding = '2px 8px';
        copyBtn.style.fontSize = '12px';
        
        onionAddress.appendChild(copyBtn);
        
        copyBtn.addEventListener('click', function() {
            navigator.clipboard.writeText(text).then(function() {
                copyBtn.textContent = 'Copied!';
                setTimeout(function() {
                    copyBtn.textContent = 'Copy';
                }, 2000);
            });
        });
    }
});