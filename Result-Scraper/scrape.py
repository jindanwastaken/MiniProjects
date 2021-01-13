# This is for CUSAT


from selenium import webdriver

from selenium.webdriver.common.keys import Keys
import xlwt
from xlwt import Workbook

import time

wb = Workbook()
sheet = wb.add_sheet('Sheet 1')

driver = webdriver.Chrome(
    executable_path=r'./chromedriver.exe')

driver.get("http://results.cusat.ac.in/regforms/exam.php")
# time.sleep(1.5)
driver.find_element_by_xpath("/html/body/table[2]/tbody/tr[4]/td/input").click()

firstRollNumber = input("Enter first roll number : ")
lastRollNumber = input("Enter last roll number : ")

count = 1
for i in range(firstRollNumber, lastRollNumber + 1):
    # time.sleep(3)
    try:
        it = driver.find_element_by_xpath(
            "/html/body/form/table/tbody/tr[2]/td[2]/input[@name='rno']")

        it.clear()
        it.send_keys(i)
        driver.find_element_by_xpath("// input[@value='O.K']").click()

    except:
        print("Error logging in for : " + i)
        continue;

    # time.sleep(3)

    try:
        name = driver.find_element_by_xpath("/html/body/table[1]/tbody/tr[2]/td/b").text
        m1 = driver.find_element_by_xpath(
            "/html/body/table[3]/tbody/tr[2]/td[3]").text
        m2 = driver.find_element_by_xpath(
            "/html/body/table[3]/tbody/tr[3]/td[3]").text
        m3 = driver.find_element_by_xpath(
            "/html/body/table[3]/tbody/tr[4]/td[3]").text
        m4 = driver.find_element_by_xpath(
            "/html/body/table[3]/tbody/tr[5]/td[3]").text
        m5 = driver.find_element_by_xpath(
            "/html/body/table[3]/tbody/tr[6]/td[3]").text
        m6 = driver.find_element_by_xpath(
            "/html/body/table[3]/tbody/tr[7]/td[3]").text
        m7 = driver.find_element_by_xpath(
            "/html/body/table[3]/tbody/tr[8]/td[3]").text
        m8 = driver.find_element_by_xpath(
            "/html/body/table[3]/tbody/tr[9]/td[3]").text

    except Exception as e:
        print(e)
        name = "0"
        m1 = "0"
        m2 = "0"
        m3 = "0"
        m4 = "0"
        m5 = "0"
        m6 = "0"
        m7 = "0"
        m8 = "0"

    try:
        gpa = driver.find_element_by_xpath(
            "/html/body/table[3]/tbody/tr[10]/td[2]/b").text

    except:
        gpa = "Failed"

    sheet.write(count, 0, name)
    sheet.write(count, 1, m1)
    sheet.write(count, 2, m2)
    sheet.write(count, 3, m3)
    sheet.write(count, 4, m4)
    sheet.write(count, 5, m5)
    sheet.write(count, 6, m6)
    sheet.write(count, 7, m7)
    sheet.write(count, 8, m8)
    sheet.write(count, 11, gpa)
    count = count+1

    print("Written for reg no :", i)
    print("Name :", name)

    driver.back()

wb.save('./results.xls')
driver.close()
