import requests
import threading
import json
import os

def get_result(dat):
    def get_plag(data,arr):
        plag_results = requests.post("https://plagiarism-api.azurewebsites.net/result", json = data, headers = {"Authorization": "Basic a29ndWw6a29ndWwxNw=="}).json()
        # plag_results = plag_results.json()
        arr.append(plag_results)

    def get_grad(data,arr):
        grad_results = requests.post("https://grading-api.azurewebsites.net/grade", json = data, headers = {"Authorization": "Basic a29ndWw6a29ndWwxNw=="}).json()
        # grad_results = grad_results.json()
        arr.append(grad_results)

    plag_arr = []
    grad_arr = []
    lang = dat['lang']
    if lang="c++":
        lang = "cc"
    plag = {
        'lang': lang,
        'files': dat['submissions']
    }
    grad = {
        'lang': lang,
        'input': dat['input'],
        'output': dat['output'],
        'submissions': dat['submissions']
    }
    n = len(dat['input'])
    threshold = int(dat['threshold'])
    x = threading.Thread(target=get_plag, args=(plag,plag_arr,))
    y = threading.Thread(target=get_grad, args=(grad,grad_arr,))

    x.start()
    y.start()

    x.join()
    y.join()

    if len(plag_arr)==1 and len(grad_arr)==1:
        plag_result, grad_result = plag_arr[0],grad_arr[0]
        plagiarized = []
        import mysql.connector
        mydb = mysql.connector.connect(
            host=os.environ['db_host'],
            user=os.environ['db_user'],
            password=os.environ['db_password'],
            database=os.environ['db']
        )
        mycursor = mydb.cursor()
        if plag_result['status'] != "Fail":
            sql = "UPDATE assignments SET report_url = %s WHERE assignment_id = %s"
            mycursor.execute(sql, (plag_result['detailed_report_url'],int(dat['assignment_id']),))
            for key in plag_result['results'].keys():
                if int(plag_result['results'][key]) >= threshold:
                    plagiarized.append(key)
                    sql = "UPDATE submissions SET grade = 0, plag = Yes WHERE student_id = %s"
                    mycursor.execute(sql, (key,))
            # mydb.commit()
            for key in grad_result.keys():
                if key not in plagiarized:
                    grade = int(round(grad_result[key]/n,2)*100) 
                    sql = "UPDATE submissions SET grade = %s WHERE student_id = %s"
                    mycursor.execute(sql, (grade, key,))

            mydb.commit()

            mycursor.close()
            mydb.close()
