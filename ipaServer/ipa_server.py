#! /usr/bin/env python3
from flask import Flask
from flask import request
from flask import jsonify
from flask import send_from_directory
from flask_cors import CORS
import json, os,zipfile, plistlib, sys, re,pymysql
import uuid, shutil, time

# https://www.jianshu.com/p/ff1b678de5bf
basehost = 'https://serverIP:port'
basedir = os.path.abspath(os.path.dirname(__name__))
app = Flask(__name__);
CORS(app, supports_credentials=True)

app.config.update(
    MAX_CONTENT_LENGTH=500*1024*1024
)
# @app.route('/')
@app.route('/upload', methods=['GET', 'POST'])
def upload():
	# get upload image and save
    uuidName = str(uuid.uuid1());

    receiveFile = request.files['package']
    filePath = basedir + '/ipas/' + uuidName + '.ipa'
    ipaDownPath = basehost + '/ipas/' + uuidName + '.ipa'
    receiveFile.save(filePath)
    plistInfo = analyze_ipa_with_plistlib(filePath);
    buildNumber = plistInfo['CFBundleVersion'];
    bundleIdentifier = plistInfo['CFBundleIdentifier']
    bundleName = plistInfo['CFBundleName']
    bundleVersion = plistInfo['CFBundleShortVersionString']
    jobName = request.values['job_name']

    f = open(uuidName,'w+')
    plistFileInfo =  general_plist(ipaDownPath,bundleIdentifier, buildNumber)
    f.write(plistFileInfo)
    f.close()
    shutil.move(uuidName,'./plists/' + uuidName)
    plistPath = basehost + '/plists/' + uuidName;
    downloadPath = "itms-services://?action=download-manifest&url=%s" % (plistPath)

    insertData(plistPath, downloadPath, buildNumber, bundleIdentifier, bundleName, bundleVersion, jobName)
#    result = {};
#    result['code'] = 1;
#    data = {};
#    data['filePath'] = filePath;
#    data['guid'] = uuidName;
#    result['data'] = data;
    return uuidName;

def insertData(plistPath, downloadPath,buildNumber, bundleIdentifier, bundleName, bundleVersion, jobName):
    conn = pymysql.connect(host='ip', user='user',password='password',database='database',charset='utf8')
    cursor = conn.cursor()

    update_sql = 'UPDATE tableName SET is_latest = 0 WHERE job_name = "%s" ' % (jobName);

    cursor.execute(update_sql);
    conn.commit();

    # 定义要执行的SQL语句
    sql = """
    INSERT INTO package_info (is_latest,plist_path ,download_path,build_number, bundle_identifier, bundle_name, bundle_version, job_name, create_time) VALUES (1, %s, %s, %s,%s, %s, %s ,%s, %s);
    """
    # 执行SQL语句
    cursor.execute(sql, [plistPath, downloadPath,buildNumber, bundleIdentifier, bundleName, bundleVersion, jobName, time.time()])
    conn.commit();
    pass

@app.route('/get_ipa_info', methods=['GET', 'POST'])
def getIpaInfo():
    # pageSize = request.values['page_size'];
    page = int(request.values['page']);
    pageSize = int(request.values['page_size']);
    infoList = query_sql(page * pageSize, pageSize);
    
    result = {};
    result['code'] = 1;
    allData = [];
    if len(infoList) > 0:
        dicKey= ('plistPath', 'downloadPath', 'buildNumber', 'bundleIdentifier', 'bundleName', 'bundleVersion', 'jobName', 'createTime');
        for data in infoList:
            dic = dict(zip(dicKey,data))
            allData.append(dic)
            pass    
        pass
    result['data'] = allData;
    return jsonify(result);

def query_sql(from_index, length):
    conn = pymysql.connect(host='localhost', user='root',password='root',database='ipa_info',charset='utf8')
    cursor = conn.cursor()
    # 定义要执行的SQL语句
    
    sql = """
    SELECT plist_path ,download_path,build_number, bundle_identifier, bundle_name, bundle_version, job_name, create_time FROM package_info where is_latest=1 order by id desc LIMIT %s,%s;
    """ % (from_index, length)
# 执行SQL语句
    cursor.execute(sql)
    info = cursor.fetchall()
    conn.commit();
    # 关闭光标对象
    cursor.close()
    # 关闭数据库连接
    conn.close()
    return info;

@app.route('/get_ipa_info_by_job_name', methods=['GET', 'POST'])
def getIpaInfoByJobName():
    # pageSize = request.values['page_size'];
    page = int(request.values['page']);
    pageSize = int(request.values['page_size']);
    jobName = request.values['job_name'];
    infoList = query_sql_by_job_name(page * pageSize, pageSize, jobName);
    
    result = {};
    result['code'] = 1;
    allData = [];
    if len(infoList) > 0:
        dicKey= ('plistPath', 'downloadPath', 'buildNumber', 'bundleIdentifier', 'bundleName', 'bundleVersion', 'jobName', 'createTime');
        for data in infoList:
            dic = dict(zip(dicKey,data))
            allData.append(dic)
            pass    
        pass
    
    result['data'] = allData;
    return jsonify(result);


def query_sql_by_job_name(from_index, length, job_name):
    conn = pymysql.connect(host='localhost', user='root',password='root',database='ipa_info',charset='utf8')
    cursor = conn.cursor()
    # 定义要执行的SQL语句
    
    sql = """
    SELECT plist_path ,download_path,build_number, bundle_identifier, bundle_name, bundle_version, job_name, create_time FROM package_info where job_name='%s' order by id desc LIMIT %s,%s;
    """ % (job_name,from_index, length)
# 执行SQL语句
    cursor.execute(sql)
    info = cursor.fetchall()
    conn.commit();
    # 关闭光标对象
    cursor.close()
    # 关闭数据库连接
    conn.close()
    return info;

def general_plist(ipa_path, bundle_identifier, bundle_version):
    demo = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>items</key>
    <array>
        <dict>
            <key>assets</key>
            <array>
                <dict>
                    <key>kind</key>
                    <string>software-package</string>
                    <key>url</key>
                    <string>%s</string>
                </dict>
            </array>
            <key>metadata</key>
            <dict>
                <key>bundle-identifier</key>
                <string>%s</string>
                <key>bundle-version</key>
                <string>%s</string>
                <key>kind</key>
                <string>software</string>
                <key>title</key>
                <string>Hestia</string>
            </dict>
        </dict>
    </array>
</dict>
</plist>
    """ % (ipa_path, bundle_identifier, bundle_version)
    return demo;


# 解析ipa
def analyze_ipa_with_plistlib(ipa_path):
    ipa_file = zipfile.ZipFile(ipa_path)
    plist_path = find_plist_path(ipa_file)
    plist_data = ipa_file.read(plist_path)
    plist_root = plistlib.loads(plist_data)
    return plist_root;

def find_plist_path(zip_file):
    name_list = zip_file.namelist()
    pattern = re.compile(r'Payload/[^/]*.app/Info.plist')
    for path in name_list:
        m = pattern.match(path)
        if m is not None:
            return m.group()


@app.route("/plists/<filename>", methods=['GET', 'POST'])
def downloader(filename):
    f = open('./plists/'+filename, 'r');
    text = f.read();
    f.close();
    return text;

@app.route("/ipas/<filename>", methods=['GET', 'POST'])
def downloaderIpa(filename):
    return send_from_directory('./ipas', filename);

if __name__ == '__main__':
    app.run(host='0.0.0.0',ssl_context=('/etc/apache2/server.crt', '/etc/apache2/server.key'));
