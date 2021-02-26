# ric-auth project

The plan is that we use the "Benefit One Platform" for user/group/organization management. But that is not ready yet.

We'll use this project as a mock of the "Benefit One Platform". And when it is ready, as a translation layer between it
and the main [ric](https://github.com/rewardz/ric) project.

# quick start

- Follow [Environment setup for Docker](https://github.com/rewardz/ric/wiki/Environment-setup-for-Docker)
- docker-compose up  ( use `RESET_DB=true docker-compose up` for the first run)

- testing data could be viewed from http://127.0.0.1:10082/admin/ . Login with "dev@rewardz.sg", and "Pass1234"

- The API documents are at:
  - http://127.0.0.1:10082/api/schema/swagger-ui/
  - http://127.0.0.1:10082/api/schema/redoc/
  
These are different UIs for the same API schema
  
- `docker exec -ti ric_auth_auth-backend_1 bash` to run usual makemigrations, shell_plus, etc

- If you want to reset the DB to its original status, run this instead:
```
RESET_DB=true docker-compose up
```

# how to build the image locally
- `docker build -t ric_auth_backend .`
