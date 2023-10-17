#!/bin/bash
python3 -m gunicorn.app.wsgiapp -b 0.0.0.0:10206 -w 1 \
--certfile /home/user01/CaritasMty_Api/SSL/equipo02.tc2007b.tec.mx.cer \
--keyfile /home/user01/CaritasMty_Api/SSL/equipo02.tc2007b.tec.mx.key \
run:app > /dev/null &
# python3 -m gunicorn.app.wsgiapp -b 0.0.0.0:10206 -w 1 \
# run:app > /dev/null &
