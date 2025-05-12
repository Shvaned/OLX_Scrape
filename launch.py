import subprocess
def Launch_Chrome():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = r"C:\selenium\chromeProfile"
    port = 9222
    command = [
        chrome_path,
        f'--remote-debugging-port={port}',
        f'--user-data-dir={user_data_dir}',
        '--no-first-run',
        '--no-default-browser-check'
    ]
    subprocess.Popen(command)
    print(f"Chrome launched with remote debugging on port {port}")
