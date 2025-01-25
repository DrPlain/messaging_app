## Messaging app
#### Solved the Kubernetes PullImageErr by
- minikuke ssh
- echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
- GRANT ALL PRIVILEGES ON messaging_app.* TO 'DrPlain-messaging_app'@'%';
