module.exports = {
  apps: [
    {
      name: 'sol-radar',
      // Point to your uvicorn executable
      script: 'uvicorn',
      // Pass the arguments you usually use in terminal
      args: 'app.main:app --host 0.0.0.0 --port 8000',
      // Ensure it uses the right interpreter (crucial for venv)
      interpreter: 'python3',
      autorestart: true,
      watch: false, // Don't use --reload in production
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: '.',
      },
    },
  ],
}
