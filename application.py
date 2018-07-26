from flask import Flask, render_template, request, send_from_directory
from flask_api import status
from werkzeug import secure_filename
import os
import pandas as pd
from geopy.geocoders import GoogleV3
import geopy
from geopy.exc import GeocoderTimedOut
geopy.geocoders.options.default_timeout = 6

UPLOAD_FOLDER = 'static/uploads'

application = app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def geocodeExtractor(string):
    try:
        location = geolocator.geocode(string, exactly_one=False)
        if isinstance(location, list):
            if len(location) > 1:
                longitude = []
                latitude = []
                lat_long = []
                for i in location:
                    latitude.append(i.latitude)
                    longitude.append(i.longitude)
                    lat_long.append(str(i.latitude) + ' , ' + str(i.longitude))
                mark = 'Multiple'
            else:
                loc = location[0]
                latitude = loc.latitude
                longitude = loc.longitude
                mark = 'YES'
                lat_long = str(latitude) + ' , ' + str(longitude)

        elif location != None:
            latitude = location.latitude
            longitude = location.longitude
            mark = 'YES'
            lat_long = str(latitude) + ' , ' + str(longitude)
        else:
            latitude = None
            longitude = None
            mark = 'NO'
            lat_long = None

    except GeocoderTimedOut:
        latitude = None
        longitude = None
        mark = 'NO'
        lat_long = None

    return (mark, latitude, longitude, lat_long)

@app.route('/<string:code>')
def main(code):
    if code == 'geocoder':
        return render_template('geocoder.html')
    else:
        return status.HTTP_404_NOT_FOUND

@app.route('/upload', methods =['GET', 'POST'])
def upload():


    if request.method == 'POST':
        global geolocator
        geolocator = GoogleV3(request.form['GoogleKey'])
        f = request.files['file']
        global df
        df = pd.read_excel(f, encoding='utf8')
        t = str(0.06*len(df))
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        return render_template('upload.html', value = t)

@app.route('/download')
def download():
    if request.method == 'GET':
        global df
        address = df['Address']
        output = []
        for i in address:
            result = geocodeExtractor(i)
            output.append((i, result[0], result[1], result[2], result[3]))
        df = pd.DataFrame(output)
        df.columns = ['address', 'location found?', 'latitude', 'longitude', 'lat_long']
        df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], 'Output Geocode.xlsx'), sheet_name='sheet1', index=False)
        return send_from_directory(app.config['UPLOAD_FOLDER'], 'Output Geocode.xlsx')

if __name__ == "__main__":
    app.run()