The application is in a docker environment so make sure your command begin with "docker compose ..."
Always run **"docker compose exec web"** followed by the python/django command.

We use the loginrequiredmiddleware so we dont need to check if the user is logged in in every function.

Never use inine javascript and insert directly into html, you have 2 options either try to do it inline with alpine or write a javascript file in the frontend and then import it with vite

Always use the grill me skill

never use django signals use django lifecycle library

