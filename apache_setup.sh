
OUTPUT=$"$(httpd -V)"

touch tmp_file.txt

for item in $OUTPUT
do
    if [[ $item =~ SERVER_CONFIG_FILE.* ]] || [[ $item =~ HTTPD_ROOT.* ]] ; then
        echo "$item" >> tmp_file.txt
    fi
done

source tmp_file.txt

ABS_SERVER_CONFIG_FILE="$HTTPD_ROOT/$SERVER_CONFIG_FILE"
HTTPD_CONFIG_DIR="$(dirname $ABS_SERVER_CONFIG_FILE)"

echo "Detected Main apache config file :${ABS_SERVER_CONFIG_FILE}"

echo "Detected Main apache config Dir :${HTTPD_CONFIG_DIR}"

rm tmp_file.txt

read -p "Is this correct? (Type 'yes' to continue, anything else to stop): " choice

if [ $choice != "yes" ]; then
    exit 0
fi

read -p "Enter Server name, (default: localhost) " servername

if [ -z $servername ]; then
    servername="localhost"
fi

sed -e "s#\[path_to_project\]#$(pwd)#g" -e "s#\[domain_name\]#$servername#" httpd-vhosts.conf.template  > template_file.txt

echo "Copying vhost file to ${HTTPD_CONFIG_DIR}/django-vhost.conf"

cp template_file.txt "$HTTPD_CONFIG_DIR/django-vhost.conf"
rm template_file.txt

echo "Backing up apache Main config file to ${ABS_SERVER_CONFIG_FILE}.BAKUP"

cp $ABS_SERVER_CONFIG_FILE "${ABS_SERVER_CONFIG_FILE}.BAKUP"

echo "LoadModule wsgi_module modules/mod_wsgi.so" >> $ABS_SERVER_CONFIG_FILE
echo "Include $(dirname $SERVER_CONFIG_FILE)/django-vhost.conf" >> $ABS_SERVER_CONFIG_FILE
