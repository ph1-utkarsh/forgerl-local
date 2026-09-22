FROM python:3.8-slim@sha256:1d52838af602b4b5a831beb13a0e4d073280665ea7be7f69ce2382f29c5a613f
RUN pip install --no-cache-dir decorator==4.3.0 future==0.17.1 six==1.12.0 python_toolbox==0.9.3 pytest==4.4.1
