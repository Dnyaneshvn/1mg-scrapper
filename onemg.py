from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
from random import randint

import concurrent.futures

MAX_THREADS = 15


def scrape_data(url):
    chrome_options = Options()
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
    df = pd.DataFrame()
    medicineDetailUrlList = []  # for detailed
    medicineImageLinkList = []
    medicineNameList = []
    medicinePriceList = []
    medicinePriceNoSignList = []
    medicineQuantityList = []
    medicinePrescriptionRequiredList = []
    medicineSaltsList = []
    medicineManufacturerList = []
    medicineQuantityCoverList = []
    medicineQuantityUnitsList = []
    medicineQuantityLastUnitList = []
    try:
        driver.get(url)
        b = randint(12, 39)
        sleep(b)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = soup.find_all('div', attrs={'class': 'style__width-100p___2woP5 style__flex-row___m8FHw'})
        products = []
        for card in cards:
            c = card.find_next('div', attrs={
                "class": 'style__product-card___1gbex style__card___3eL67 style__raised___3MFEA style__white-bg___10nDR style__overflow-hidden___2maTX'})
            cardData = c.find('a')
            medicineLink = cardData['href']
            medicineFinalLink = 'https://www.1mg.com' + medicineLink
            medicineDetailUrlList.append(medicineFinalLink)
            productImage = cardData.find_next('img')['src']
            medicineImageLinkList.append(productImage)

            isPrescriptionRequired = False
            i = 1
            for jk in cardData.find(attrs={'class': 'style__flex-1___A_qoj'}):
                if i == 1:
                    medicineName = jk.find_next('div').get_text()
                    medicinePrice = jk.find_next('div').find_next('div').get_text()

                    # Removing MRP
                    medicinePrice = medicinePrice[3:]
                    medicinePrice = medicinePrice[0] + ' ' + medicinePrice[1:]
                    medicinePriceWithoutSign = medicinePrice.split(" ")[1]

                    # Saving to List
                    medicineNameList.append(medicineName)
                    medicinePriceList.append(medicinePrice)
                    medicinePriceNoSignList.append(medicinePriceWithoutSign)

                elif i == 3:
                    # Add conditions to separate quantity accordingly
                    medicineQuantity = jk.find_next('div').get_text()
                    medicineManufacturer = jk.find_next('div').find_next('div').get_text()
                    medicineQuantityList.append(medicineQuantity)
                    medicineQuantityFinalList = medicineQuantity.split("of")
                    if medicineQuantityFinalList[0].strip() == 'strip' or medicineQuantityFinalList[
                        0].strip() == 'packet' or medicineQuantityFinalList[
                        0].strip() == 'box':
                        medicineQuantityCover = medicineQuantityFinalList[0]
                        tempHolding = medicineQuantityFinalList[1].strip().split(" ")
                        medicineQuantityUnits = tempHolding[0]

                        medicineQuantityLastUnit = ''
                        for a in tempHolding:
                            # print(medicineQuantity,a)
                            if a.endswith("es") or a.endswith("et") or a.endswith("ets") or a.endswith('ons') or a.endswith("ule"):
                                    medicineQuantityLastUnit = a

                        # medicineQuantityLastUnit = tempHolding
                        if len(medicineQuantityLastUnit) > 4:
                            medicineQuantityUnitsList.append(medicineQuantityUnits)
                            medicineQuantityCoverList.append(medicineQuantityCover)
                            medicineQuantityLastUnitList.append(medicineQuantityLastUnit)
                        else:
                            if medicineQuantityCover == 'packet':
                                medicineQuantityCoverList.append('packet')
                                medicineQuantityLastUnitList.append(tempHolding[len(tempHolding)])
                            medicineQuantityUnitsList.append("-")
                            medicineQuantityCoverList.append("-")
                            medicineQuantityLastUnitList.append("-")
                    else:
                        listOfQuantityWords = medicineQuantity.split(" ")
                        medicineQuantityUnitsList.append("-")
                        medicineQuantityCoverList.append(listOfQuantityWords[0])
                        medicineQuantityLastUnitList.append("-")
                    medicineManufacturerList.append(medicineManufacturer)
                else:
                    if i == 2:
                        if jk.get_text() == 'Prescription Required':
                            isPrescriptionRequired = True
                        elif jk.get_text() == '':
                            isPrescriptionRequired = False
                        medicinePrescriptionRequiredList.append(isPrescriptionRequired)
                    else:
                        salts = jk.get_text()
                        salts = salts.replace("ADD", '')
                        medicineSaltsList.append(salts)
                i = i + 1
        df['name'] = medicineNameList
        df['price'] = medicinePriceList
        df['priceNoSign'] = medicinePriceNoSignList
        df['prescriptionRequired'] = medicinePrescriptionRequiredList
        df['detail_quantity'] = medicineQuantityList
        df['covers'] = medicineQuantityCoverList
        df['quantity'] = medicineQuantityUnitsList
        df['units'] = medicineQuantityLastUnitList
        df['manufacturer'] = medicineManufacturerList
        df['prodLink'] = medicineImageLinkList
        df['salts'] = medicineSaltsList
        df['prodUrl'] = medicineDetailUrlList


    except:
        print("Exception Occureed");

    finally:
        driver.close()
        driver.quit()

    return df




if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--ignore-gpu-blocklist")
    chrome_options.add_argument("--disable-software-rasterizer")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
    str1 = driver.capabilities['browserVersion']
    str2 = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
    print(str1)
    print(str2)
    names = []  # List to store name of the product
    urls = []  # List to store price of the product

    alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
                'v', 'w', 'x', 'y', 'z']
    driver.get("https://www.1mg.com/drugs-all-medicines?label=a")

    mainAlphabetUrls = []

    # first we make 26 links for the alphabet
    for a in alphabets:
        mainAlphabetUrls.append("https://www.1mg.com/drugs-all-medicines?label=" + a)
        print(mainAlphabetUrls[len(mainAlphabetUrls) - 1])


    # We then fetch 26 last page numbers for those links
    lastPageNumbers = [
        1072,
    309,
    1007,
    589,
    455,
    389,
    378,
    150,
    241,
    65,
    197,
    489,
    682,
    441,
    472,
    648,#p
    48,
    621,
    609,
    628,
    115,
    327,
    89,
    73,
    26,
    289]
    # for url in mainAlphabetUrls:
    #     driver.get(url)
    #     sleep(randint(2, 10))
    #     soup = BeautifulSoup(driver.page_source, 'html.parser')
    #     my_table = soup.find('ul', attrs={'class': 'list-pagination'})
    #     i = 0
    #     for tag in my_table:
    #         if i == 6:
    #             lastPageNumbers.append(int(tag.get_text()))
    #             print(tag.get_text())
    #         i = i + 1

    print(len(lastPageNumbers))
    updatedUrlsWithPage = []
    sleepCounter = 0
    pages_per_csv = 25
    if __name__ == '__main__':
    # Your existing code here...
        if __name__ == '__main__':
    # Your existing code here...

            for j in range(len(alphabets)):
                print(f"Alphabet is {alphabets[j]}")
                lastPage = lastPageNumbers[j]
                if lastPage == 0:
                    print(f"No data found for alphabet {alphabets[j]}")
                    continue  # Skip to the next alphabet if no data found
                iterationsCount = (lastPage//pages_per_csv) 
        
                urls = []
                counter=0
                print(f"Last Page Number is : {lastPageNumbers[j]}")
                for i in range(1,lastPageNumbers[j]+1):
                    urls.append(f'https://www.1mg.com/drugs-all-medicines?page={i}&label={alphabets[j]}')
                    if(i%pages_per_csv==0):
                        counter+=1
                        sleepCounter+=1
                        print("Hii Before")
                        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                            # Submit a task to get the data from each URL.
                            futures = [executor.submit(scrape_data, url) for url in urls]
                            # Wait for all of the tasks to finish.
                            results = [future.result() for future in futures]
                        results_df = pd.concat(results)
                        results_df.to_csv(f'{alphabets[j]}{counter}.csv',encoding='utf-8')
                        print("Hii")
                        urls=[]
                        sleep(randint(2, 10))
                        if(sleepCounter %5 == 0):
                            print("Yo")
                            sleep(randint(60,150))
                        print(f'Counter is {counter}')
                        print(f'Iteration Count is {iterationsCount}')
                        if counter == iterationsCount:
                            #calculate if pages are left
                            #same above iteration for that
                            for i in range((counter*pages_per_csv)+1,lastPageNumbers[j]+1):
                                urls.append(f'https://www.1mg.com/drugs-all-medicines?page={i}&label={alphabets[j]}')
                                if(i%(lastPageNumbers[j])==0):
                                    counter+=1
                                    print("Hii in Last")
                                    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                                        # Submit a task to get the data from each URL.
                                        futures = [executor.submit(scrape_data, url) for url in urls]
                                        # Wait for all of the tasks to finish.
                                        results = [future.result() for future in futures]
                                    results_df = pd.concat(results)
                                    results_df.to_csv(f'{alphabets[j]}{counter}.csv',encoding='utf-8')
                                    print("Hii Last")
                                    urls=[]
                                    sleep(randint(2, 10))




    # df.to_csv(f'${alphabets[index]}.csv', index=True, encoding='utf-8')

