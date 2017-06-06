# Generating a Test Competition Bundle

<h4>Run this command in the same directory as `manag.py`. This same directory should also have `package.json` in it.</h4>

`docker exec -it django python manage.py competition_zip_name`

<h4>Available command line arguments</h4>

| Name | Alternative | Default | Description |
| --- | --- | --- | --- |
| --numphases | -p | 5 | Number of phases to create |
| --phaselength | -1 | 10 | How many minutes you would like the phase to last
| --delete | -d | True | Don't delete the temp files |
| --automigrate | -a | False | Enable auto migration between phases |

<h4>Examples</h4>

`docker exec -it django python manage.py -p 6 -1 9 -d False -a True competition_zip_name`

`docker exec -it django python manage.py --numphases 6 --phaselength 9 --delete False --automigrate True competition_zip_name`
