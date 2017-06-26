docker build . -t test
docker run -dt --name test -p 80:80 test
