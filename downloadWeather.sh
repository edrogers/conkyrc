#!/bin/bash

rm -f ~/.cache/weather.xml_NEW
curl -s https://query.yahooapis.com/v1/public/yql -d q="select * from weather.forecast where woeid=2443945" -d format=xml > ~/.cache/weather.xml_NEW
size=$(du ~/.cache/weather.xml_NEW | grep -o '^[0-9]\+');
if [ $size -ge 6 ];
then
    mv ~/.cache/weather.xml_NEW ~/.cache/weather.xml
else
    rm -f ~/.cache/weather.xml_NEW
fi

exit
