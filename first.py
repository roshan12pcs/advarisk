import requests
from lxml import html
import urllib.parse
import re
from data import data1,data2, data3, data4, data5, data6
from bs4 import BeautifulSoup
session = requests.Session()
cookies = {
    'ASP.NET_SessionId': 'd5ihsd01gyiyz12yzawvsyoq',
    'NSC_fqbokjzbo_jqw4': 'ffffffff094eed2545525d5f4f58455e445a4a423660',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

response = requests.get('https://epanjiyan.rajasthan.gov.in/e-search-page.aspx', headers=headers)
with open("e_search_page.html", "w", encoding="utf-8") as file:
    file.write(response.text)


tree = html.fromstring(response.content)
view_state = tree.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
even_id = tree.xpath('//input[@id="__EVENTVALIDATION"]/@value')[0]
state_generator = tree.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]

from bs4 import BeautifulSoup

def get_new_data(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'ctl00$hdnCSRF'})
    
    if not csrf_input:
        print("Input tag not found.")
        return None
    
    next_text = csrf_input.next_sibling
    while next_text and (not hasattr(next_text, 'string') or next_text.string is None):
        next_text = next_text.next_sibling  # Skip over tags/comments
    
    if next_text and next_text.string:
        return next_text.string.strip()
    else:
        print("No text found after input.")
        return None


# print(view_state)
# print(even_id)
# print(state_generator)



view_state_encoded = urllib.parse.quote_plus(view_state)
even_id_encoded = urllib.parse.quote_plus(even_id)

# First update VIEWSTATE block
updated_data = re.sub(
    r'__VIEWSTATE=.*?&__VIEWSTATEGENERATOR',
    f'__VIEWSTATE={view_state_encoded}&__VIEWSTATEGENERATOR',
    data1
)

# Then update EVENTVALIDATION block
updated_data = re.sub(
    r'__EVENTVALIDATION=.*?&ctl00%24ContentPlaceHolder1%24a',
    f'__EVENTVALIDATION={even_id_encoded}&ctl00%24ContentPlaceHolder1%24a',
    updated_data
)

# print(updated_data)

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://epanjiyan.rajasthan.gov.in',
    'Referer': 'https://epanjiyan.rajasthan.gov.in/e-search-page.aspx',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'X-MicrosoftAjax': 'Delta=true',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}
response1 = session.post('https://epanjiyan.rajasthan.gov.in/e-search-page.aspx', headers=headers, data=updated_data)
with open("e_search_page_rural.html", "w", encoding="utf-8") as file:
    file.write(response1.text)
tree = html.fromstring(response1.content)


soup = BeautifulSoup(response1.text, 'html.parser')

csrf_input = soup.find('input', {'name': 'ctl00$hdnCSRF'})
if csrf_input:
    next_text = csrf_input.next_sibling
    while next_text and next_text.string is None:
        next_text = next_text.next_sibling  # Skip over other tags/comments
    if next_text:
        new_data = next_text.strip()
        # print(new_data)
    else:
        print("No text found after input.")
else:
    print("Input tag not found.")
with open("data1.txt", "w", encoding="utf-8") as file:
    file.write(next_text)


def extract_viewstate_value(s):
    start_token = "__VIEWSTATE|"
    start_index = s.find(start_token)
    if start_index == -1:
        return None  # not found
    
    # Move index right after the start token
    start_index += len(start_token)
    
    # Find the next "|" after start_index
    end_index = s.find("|", start_index)
    if end_index == -1:
        # No ending pipe found, return till end of string
        return s[start_index:]
    
    # Extract the substring between start and end
    return s[start_index:end_index]

def extract_ev_value(s):
    start_token = "|__EVENTVALIDATION|"
    start_index = s.find(start_token)
    if start_index == -1:
        return None  # not found
    
    # Move index right after the start token
    start_index += len(start_token)
    
    # Find the next "|" after start_index
    end_index = s.find("|", start_index)
    if end_index == -1:
        # No ending pipe found, return till end of string
        return s[start_index:]
    
    # Extract the substring between start and end
    return s[start_index:end_index]

# Example usage

result = extract_viewstate_value(new_data)
eval = extract_ev_value(new_data)
# print(eval,"result###############")
dist = 1
data2= data2.replace("District=1","District=1")


result = extract_viewstate_value(new_data)
eval = extract_ev_value(new_data)
view_state_encoded = urllib.parse.quote_plus(result)
even_id_encoded = urllib.parse.quote_plus(eval)

# First update VIEWSTATE block
updated_data = re.sub(
    r'__VIEWSTATE=.*?&__VIEWSTATEGENERATOR',
    f'__VIEWSTATE={view_state_encoded}&__VIEWSTATEGENERATOR',
    data2
)

# Then update EVENTVALIDATION block
updated_data = re.sub(
    
    r'__EVENTVALIDATION=.*?&__ASYNCPOST',
    f'__EVENTVALIDATION={even_id_encoded}&__ASYNCPOST',
    updated_data
)


response1 = session.post('https://epanjiyan.rajasthan.gov.in/e-search-page.aspx', headers=headers, data=updated_data)
with open("e_search_page_rural_new.html", "w", encoding="utf-8") as file:
    file.write(response1.text)


new_data = get_new_data(response1.text)

result = extract_viewstate_value(new_data)
eval = extract_ev_value(new_data)
# print(eval,"result###############")

result = extract_viewstate_value(new_data)
eval = extract_ev_value(new_data)
view_state_encoded = urllib.parse.quote_plus(result)
even_id_encoded = urllib.parse.quote_plus(eval)

print(even_id_encoded)
# First update VIEWSTATE block
updated_data = re.sub(
    r'__VIEWSTATE=.*?&__VIEWSTATEGENERATOR',
    f'__VIEWSTATE={view_state_encoded}&__VIEWSTATEGENERATOR',
    data3
)


# Then update EVENTVALIDATION block
updated_data = re.sub(
    
    r'__EVENTVALIDATION=.*?&__VIEWSTATEENCRYPTED',
    f'__EVENTVALIDATION={even_id_encoded}&__VIEWSTATEENCRYPTED',
    updated_data
)


response1 = session.post('https://epanjiyan.rajasthan.gov.in/e-search-page.aspx', headers=headers, data=updated_data)
with open("e_search_page_rural_new3.html", "w", encoding="utf-8") as file:
    file.write(response1.text)


new_data = get_new_data(response1.text)

result = extract_viewstate_value(new_data)
eval = extract_ev_value(new_data)


view_state_encoded = urllib.parse.quote_plus(result)
even_id_encoded = urllib.parse.quote_plus(eval)

print(even_id_encoded)
# First update VIEWSTATE block
updated_data = re.sub(
    r'__VIEWSTATE=.*?&__VIEWSTATEGENERATOR',
    f'__VIEWSTATE={view_state_encoded}&__VIEWSTATEGENERATOR',
    data4
)


# Then update EVENTVALIDATION block
updated_data = re.sub(
    r'__EVENTVALIDATION=.*?&__VIEWSTATEENCRYPTED',
    f'__EVENTVALIDATION={even_id_encoded}&__VIEWSTATEENCRYPTED',
    updated_data
)
response1 = session.post('https://epanjiyan.rajasthan.gov.in/e-search-page.aspx', headers=headers, data=updated_data)
with open("e_search_page_rural_new4.html", "w", encoding="utf-8") as file:
    file.write(response1.text)


new_data = get_new_data(response1.text)

result = extract_viewstate_value(new_data)
eval = extract_ev_value(new_data)
# print(eval,"result###############")

result = extract_viewstate_value(new_data)
eval = extract_ev_value(new_data)
view_state_encoded = urllib.parse.quote_plus(result)
even_id_encoded = urllib.parse.quote_plus(eval)

print(even_id_encoded)
# First update VIEWSTATE block
updated_data = re.sub(
    r'__VIEWSTATE=.*?&__VIEWSTATEGENERATOR',
    f'__VIEWSTATE={view_state_encoded}&__VIEWSTATEGENERATOR',
    data5
)


# Then update EVENTVALIDATION block
updated_data = re.sub(
    r'__EVENTVALIDATION=.*?&__VIEWSTATEENCRYPTED',
    f'__EVENTVALIDATION={even_id_encoded}&__VIEWSTATEENCRYPTED',
    updated_data
)

document_id = 17
document_name = 'Sale Deed'
document_num = 10

updated_data = updated_data.replace(f'ctl00%24ContentPlaceHolder1%24ddldocument=17',
                                        f'ctl00%24ContentPlaceHolder1%24ddldocument={document_id}')
updated_data = updated_data.replace(f'ctl00%24ContentPlaceHolder1%24txtclaiment=10',
                                        f'ctl00%24ContentPlaceHolder1%24txtclaiment={document_num}')
print(updated_data,"updated data")
response_new = session.post('https://epanjiyan.rajasthan.gov.in/e-search-page.aspx', headers=headers, data=updated_data)
with open("e_search_page_rural_new4444.html", "w", encoding="utf-8") as file:
    file.write(response1.text)

tree = html.fromstring(response1.content)
image_url = tree.xpath('//img[@id="ContentPlaceHolder1_Image1"]/@src')[0]
image_url = "https://epanjiyan.rajasthan.gov.in/"+image_url.replace(" ","%20")

print(image_url)


response = requests.get(image_url)

# Check if the request was successful
if response.status_code == 200:
    # Define the file path to save the image locally
    file_path = "downloaded_image.jpg"  # You can change this to any desired filename

    # Open the file in write-binary mode and save the image content
    with open(file_path, 'wb') as file:
        file.write(response.content)
    
    print(f"Image downloaded and saved as {file_path}")
    
    # Get input from the user
    user_input = input("Enter any input to continue: ")

    # Print the image URL
    print(f"The image URL is: {image_url}")
else:
    print(f"Failed to download image. Status code: {response.status_code}")

new_data = get_new_data(response_new.text)

result = extract_viewstate_value(new_data)
eval = extract_ev_value(new_data)

view_state_encoded = urllib.parse.quote_plus(result)
even_id_encoded = urllib.parse.quote_plus(eval)


# print(even_id_encoded)
# First update VIEWSTATE block
updated_data = re.sub(
    r'__VIEWSTATE=.*?&__VIEWSTATEGENERATOR',
    f'__VIEWSTATE={view_state_encoded}&__VIEWSTATEGENERATOR',
    data6
)




# Then update EVENTVALIDATION block
updated_data = re.sub(
    r'__EVENTVALIDATION=.*?&__VIEWSTATEENCRYPTED',
    f'__EVENTVALIDATION={even_id_encoded}&__VIEWSTATEENCRYPTED',
    updated_data
)


data = {
    'ctl00$ScriptManager1': 'ctl00$upContent|ctl00$ContentPlaceHolder1$btnsummary',
    'ScriptManager1_HiddenField': '',
    'ctl00$ContentPlaceHolder1$a': 'rbtrural',
    'ctl00$ContentPlaceHolder1$ddlDistrict': '1',
    'ctl00$ContentPlaceHolder1$ddlTehsil': '1',
    'ctl00$ContentPlaceHolder1$ddlSRO': '1',
    'ctl00$ContentPlaceHolder1$ddlcolony': '-Select-',
    'ctl00$ContentPlaceHolder1$ddldocument': '17',
    'ctl00$ContentPlaceHolder1$txtexcutent': '',
    'ctl00$ContentPlaceHolder1$txtclaiment': '10',
    'ctl00$ContentPlaceHolder1$txtexecutentadd': '',
    'ctl00$ContentPlaceHolder1$txtprprtyadd': '',
    'ctl00$ContentPlaceHolder1$txtimgcode': user_input,
    'ctl00$hdnCSRF': '',
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__LASTFOCUS': '',
    '__VIEWSTATE': result,
    '__VIEWSTATEGENERATOR': '59A5EC9F',
    '__SCROLLPOSITIONX': '0',
    '__SCROLLPOSITIONY': '0',
    '__EVENTVALIDATION': eval,
    '__VIEWSTATEENCRYPTED': '',
    '__ASYNCPOST': 'true',
    'ctl00$ContentPlaceHolder1$btnsummary': 'View Summary',
}

print(data)


response = session.post('https://epanjiyan.rajasthan.gov.in/e-search-page.aspx', headers=headers,
                                 data=data,  allow_redirects=True)
with open("e_search_page_rural_new10.html", "w", encoding="utf-8") as file:
                 file.write(response.text)



data = 'ctl00%24ScriptManager1=ctl00%24upContent%7Cctl00%24ContentPlaceHolder1%24gridsummary&ScriptManager1_HiddenField=&ctl00%24ContentPlaceHolder1%24a=rbtrural&ctl00%24ContentPlaceHolder1%24ddlDistrict=1&ctl00%24ContentPlaceHolder1%24ddlTehsil=1&ctl00%24ContentPlaceHolder1%24ddlSRO=1&ctl00%24ContentPlaceHolder1%24ddlcolony=-Select-&ctl00%24ContentPlaceHolder1%24ddldocument=17&ctl00%24ContentPlaceHolder1%24txtexcutent=&ctl00%24ContentPlaceHolder1%24txtclaiment=10&ctl00%24ContentPlaceHolder1%24txtexecutentadd=&ctl00%24ContentPlaceHolder1%24txtprprtyadd=&ctl00%24ContentPlaceHolder1%24txtimgcode=&ctl00%24hdnCSRF=&__EVENTTARGET=ctl00%24ContentPlaceHolder1%24gridsummary&__EVENTARGUMENT=Page%242&__LASTFOCUS=&__VIEWSTATE=XVC5SeN51Pentf1213K7eV4iIZ1q8zkT%2FQIjFvpgoZo12w0Z3ERlxeYJo5jlSwF3YCyiL5O4rnX2tkMohmX8Lx5FeKUkGNGxZuRmXlKQVxADtAe70RiGAZfC91xYbu7Zw8HZMPoD%2FCQ3jEa6ywR%2FLArihjv9vKtKt1V9Zy9Zvgcg7f%2FU%2F6nUx20kFK0StlB%2BrLWx6TqeThE7QbLMIdYP4PW7abl7Cqg4aVjF6IhUrZTeCW9J0UOQZu2USZHAgjLjE26uYnIa1qtqdGC1pQt9NNgGuNkOPs984Dl91AUzMoVjDPLDH0ahdlXR0ObYh0DkhQPoFUn%2F%2FTmve2GVruB6lZpFOwxDwCD1ElFwt9HK5fY4eseH5EOc5bSn4GrkNj%2FqyqTCDJNpHtIXt1TKq0SyUwiWqH5NEys44G1ND%2BxX0AxW5w6kAigWVWzpcoqlr6IY7kPX6j3JOiI1wMQOQ4Z2ENm4KZiHtbN8K%2F2Tqto6Zmz2GW7jOF2MJXZbyhLeJiRNd3eBI0smIZQvlpPU%2FQQxkMb7Qepn5Mz6H6ptjsQSWwGVR0UzZ%2Bs99w%2B8yY8Ywg4rkeEV4ApdD0y%2BHgPjkD05FfIvSGqU87h74PbfbUwWdKgM09bEyyPxCjghfgYxyDI%2BZFjV%2Bo2XHN%2BfTAXAWruhZteV2YDFW3tduTzFrcxeIShU3RszdTl6c25O221YtMti7nSKy9cxNu4XM4%2BSJljue91OTV%2BeUFRtXe%2Fs2V6X8XuJUr2YGd9DDcVrEpDsxlegS0F6fmBAkjUnoOAc7O3KaEr78KaYs%2F6dn42EcxK58kcbKOOvYltT3ou15wCDtLeW49JYIhFYuQanVdduy0I%2FkQhsjE9CUgG1Z1MaR%2Fuau1dfaS2ncAHUwoOMSwgDZ6Npwnpbro%2Bxm%2F77KfIDbuNKn4Y0RQGKlSPncDJo9s9GYA0YagErNQCDXnF5BVTujBEuNjoPJT6uvOPPuw9yLPZWje%2F3D0pNPVbGRX%2FW39xUw%2B2tv9EEXBwh3l%2BTNon%2Bkpxg8ow%2FdmGPVNW61Y6Bz49JMg6r1mGHTaasY8jX5ZVoNsZvI1b0pgc0sO7wANVOloBIq1Krq5u2G1jeOVPcSsPybIiPrkYyzgsUVVE%2Bmrt4Z8FNMpeWaUHwJ%2Bc0w0Q7vk5R1phJEaiBByKiMr5ZxjMDCoWfUVbN0FU71xExf%2Frx0QdsWzqPuGGbvXtnXHdoTlP6ae12hmw%2BJkl2hMYap0FBjohS8tOe8ZuPdHdp%2F2DxtRTSLvaEExoynjIaBRUsb9lxjKQ%2B2wsYvkQadDMYlLmmDVKqDU%2Bd4sgHU0scDX5PEUDl%2BXUg%2Fa165tf0m1ouuXychdADEu%2Bo7Vk3OtFntTGmuvNSJ3LXD4wzcbR4QoJFDQsRgyemOYgTsbIV7FZ8raxjZeZQOC%2BC3WwveyPVYYhLvEX8sOWr%2B8t639VJL%2B5rV3JyPp7AWOq6Nfo92qbtwIxEFMIoVQda0Y4kxnlLMKCL8mv2tCcGOKP5TiDRn0I9jlFc3MfZ84Pvz4eaSD75C50sj6B9lfG8HwAI%2F8v8UTLjMw0My4iiPfRUKTjOG5%2FYGvNTeQW%2B0fTdl%2Fq7zieAbT8LV72W1gtW6Yt%2B3aDMyV5ATCqwjrchwooL2ts4uopUwsR9Jy8LOCpWKSeyberVIZ9BOss1z%2BFgS3BGAdSRt%2Fy1T9fuHdyludpMc1aNHLBGanqYmLUyDUR8Nq1O0aCPCLq9B4v7vfKndvzXpJ4qkthdTM7kIb0aazQCaQqC6jMB7MDIRuDmNdBcNKfd2It9QfRnJGhWFzf2myyCEheiT3IjXkPVKPdzrI3Eyo%2FphugStGyrnrrgAUlkmc%2BuvQkowNJWXPOzmdRsdaEEDq5BvfZ2N02ZU7gvOSN1GHDW0b0yGOq8nJYjv4nagiPzsFkuFmd2vkQ%2FHvVo99dFwROMgWsu%2BW%2Bs6oL9q6Q7o7hlOavm7%2BRX2L4Y1OF9LW8VwIkuFwNQOAFaBR81nKdjYjf0YLUXmSllQKj7y%2BWEdoO%2BbaOaeTjTaZiO3eWCPbBv9HZclOnlpFfVTGfq7cvNt4%2FG1zVLcI7OvrkqlN%2BU0aAaEbYG%2BTCjVOcpDZBJ1%2FBFC08E%2BJkahLXeFLpnrSCqo8HLqbghYi1KpjMxkxMSHQZLkzHdW6W5VMeMH7FPNs96HErm5X%2FPijqgGaVGoBrR9kxohIZV%2FzYLG6Qa%2FsysJq34ELuKhAIOg6S6kHiuRhPKpIs8MvJCni%2FJs1ceTBSh9X1fqmrx0%2FAvgMUm62D3UyacW%2F%2Bkg5znoTZ6jEZiZleGpNOApJF%2BudH2RSMCw5nRPXLJntqxOS4npSVrZYDSmrutNV8qFc2m0MWexSuhGYpnP24IMpWNb%2F7ndITMJnUIFH65jMeHt9KnZp9fD9xXMPhN1lqy7NspVQsuHZVgU%2BY%2BBrZ7wXUDH47iQwwnN4DDYbRUWwQLIQUDYvf%2B5U5BwZ1HDX%2FInZkmm6%2B0h%2F%2FnFYQccZWZf6hWKsLlTxE9%2BXjZeSFyyLeisjwqdIP%2FY9jihP3JYSymR7GJNKTHGdLBIVr8qfH91awlxZO6ial5cNfzlVRAcdW9y0qtiuxFsBz1cxJIScQ7YLZOJQBMGC5hJrraJcLZHqDKQQ%2FWkeirxfQ%2FvropQ7Gu%2BpSgT7psTRirGWJT2afRIBGElu6V84MFfdCy4ywmJS2RPWZEE9J1PraAbb5kK%2B5BCfUBK%2FSaUBxlaofaUXsFxJkaMfKVGC9wjtK7SmJB2TbTwZ%2FB1fw4JRdoXgrqeFaJEpcfQUSAbPnFfX5ByOc5ro7yBmm2SyrMs7NO%2Fe56o%2FmsLb1FYeb5BqJ4mZqKiqUH%2B%2BnWuDx3VcE3Tt9erHzw7CINc6qdmQyLdE2rOg%2Fuwf%2FibscuIlyGGQcYfOAlevXHWYp4krj8UTN2AUEV2%2FHjeHFVldRargRB8dBheQ77hC1A6V%2FqhzxaAzaWq120o%2Fq6zew%2BNsyVCywb%2F4uJ1zcTlFlEfGDkalnbzvjwOAnQqLWFnhh%2FkbQMcyUThch20jQk4QFdB55OkjwaC%2F3eGNLMc3xSkaV5k%2Bha%2BUqYtg3PQg1ijElf%2FwBCHLf8hbUrrfLlLF672rR4aW0k3E7XWISvtCX7WuL8s3V0szvlpN6vCNQuv2Pg7g5ChqqYmAxsZaov5qJxWRHgtVaezOG392%2BG6LZh4SIV1pa1V0GzqONvhaC6BDbf74SWqkpUEkLFSpqRK888dErXhWb9XigcyN0XuMNTkQpfKlLMbrwxj7fxrvIifGLcm8PEmxBFRGZtmJN7jEfu9C1OZtidk4RvReiRqEENWPyxi4HJTKaLServd%2FEoFJvV3RmdY0y7GJrkFXxeWS0WrD8CKptmifpY1d41VBo%2BA74G1nw%2BvQsfnIu5aoc5sIR%2BJiXxv1KheNyUFzLKLlUse8nwlDPksbO11PcKnxgv5g1Dl%2FYTsFkecLDLdN27dZWbAPp65GfxLWwyRPO2cTzRSThI%2FseGUYgkC94MKIe18%2FyVNZDACGVCGVOvOky1DZFZJenX0ZAnk1Yty3H%2B2J%2F2XpEUgGZ9YsksdRBmwudLonYVeRdZTDNmvBQZKJIBtXTFb7jzXGgNtPs1PS8WPJ0ByQtv32x7BiqrhwGF6yb%2FZRx8XbgkyGEMXv9LEGMoQByCqn3FxCUVtWYOfmQmgMZd0XrTzoobjnWi3Z2Ce5FiAYE4oePBE8%2FeY0l6odH%2F%2BVRSb0lReUm87iqKw9BLeg9iBiBk89XePw%2FtQDvh%2BorwCU8psLCKfV8iWkRlsyKE3%2BYASLWXFx5bmIYF64rnbkwpdt%2BNmWwUzqEjBB%2BO22KjIthLBGQ4Gty9jfTGa9ragwYgZSK2VXZQOp5dumBN4KPdYCz4ybQu31AE4Vpb5MBTSk0ZBzL%2BdKMzALgS3a8byFKLa8dPfwvV2KpA1pSEQeXwFetYr9xVMyBHltPSJjtmUYNs%2FAhPEY7nr1MWdkgFwhI2DrbqTUuKFnOPqrJjKjOrhsZAznYyP9b4wfZkv6oKUC%2B5oZk7YWb0bw5UBrENL6sRlLn%2FNyyaZHhrdZ3vsDUKbP5YBB4gukaAiAWA%2FXeSOGID9zADgUlUt7mogq%2B26kAxkDZBTf8nIIBefNtB8hgnBS79Sqz7BF0xNxnrUjirDY0dIcn249P%2FITpRpCL35%2Fl6TKykeHi4LZNXlLuboI48gJ0pJ%2FT4nPKjSzRG791i19W9lfJJRIDRi656NZt%2FVIQtW23%2Be4p4bH6jHtKliRE7Bg%2BH%2BX6LDOq7n6PS2JFSeiQI8Xw49JYIEV6RkzDcUzB8%2ByCabLJQgIbLgtKID5P9kMW17bi0NQz%2FjYkhDbF2FLu3Mb73jm4mTDEnRo1jBZiCokBN8JEzaYFnHB%2FUErSgxuE2Gzvgz3Tg6J2qlgKFR6Yu1ug946SBPQ9YKfH%2BGQgKexSEm9nvX%2BSHClq%2BpMx9fRjgjGEQ4LKVUe6KJ0sD%2Fpyz56xNsB2HiQhIyzgMuJL9YO2gzD1hvan1N9R84IagxkDJms1QNBZg9nVbsoy26zoSufs92xNZxCDYmxIcWMRMny9R1zPBO8bxZpfL78G2d4cuyVt4G3hSc%2FOlQF0i%2B7EG1%2BgJ0WgbFM0YHOcpZZAJD3nQXGSnla66fuGR8xs%2By%2BrRBbh83aQyiXVYNdD0eFs5tEkQFJ3xtdi0ksOqwUm6%2Fu9lXsS%2FNsUtj6D2YqjPQ5qC0eV6qzO9zXkpGusvzJ83QCb%2FEAQYB2cfJHohei0XZ4kuSdjGz1SlfF2UfJhXRftUNXmCz7zrNNrcyl9JdZb7a1YWXtxL8f1kuN%2B0c7ZoxkQFufm2FgzsQ7gBF%2BfQdKa%2Btogy7XEFYHHnFiU%2BtsBOWRoCGR0otauCw1NTn%2FAEHJG5UyP3NRje5N4vSKHQyyYrFp4bW6GxBCUfkRpujt1yJqBKxz7SVnvkV0NQ8SGS2Nd9jcXPuqYdmuyrfuCEiq3zT1nxUwY62yCLwP20agxyv7F2K287W9QQYarCpyw6WRgJp1zp0iAdhxLHUQ4aVqjn6AZiBVTBQ8SIbO3eKoH8GD8q1UJF9f0mqVOvHBtChljFq5SRhcANhKlYD2Oj8W5fez05CaC%2BEgMifdzS0PwR6Dfm8E%2FKf11ThXesqdWnZPJsb6hKIgkSAfP5CatcrfUuKyCMab5RUd7juvbMk9%2BLyXUfHmTCS9za53mCBmJFEPSFv%2FZsF5Nr1Sd8qrHrxn%2BcPzy9HKq3XZuhm2MKC%2FnJWFwJ8p%2F8W0pM71T5SF0JF6%2BaaDm5OrfkARcRewrhLnDuwUOc6802qGssEdVU4y2HqnpNo29RbTjMX1v7SAqh1Kklspse5GVMu%2F%2FZkxMWiH2HQQlCbmsZpJltiQ8pBPRfewCD6uLi%2FmmC0P0OZ58GEo3SUoOUhQVns1OtFPDHcElygVbMJYNxCY4vIBmz2EmsirdTLP9V2JQS4mLWuqgKETMVferv4pHIykA9ZBDYfbWJcuDAwbmRV107J%2BAgfapyDvMzSpLfdNBMRiKdvBmXwU4HRFONCj94v%2F0QD86ewpUf91W5EX3tsXtAf%2FPhOjVuY5SRoRKr%2Bwhx9ghH7WfWT9IIgp0ukQZPU%2BqufA4UBszJyDMW4UYpVViNxRpiDmgUCKoAxxqix0taThGchUgus7yJw%2BIMXJGHfx5d4jhX0LiE%2BBDnqiNS%2BhgbU105u%2BIDuIgtwjpobWgJemnGDDzBUh3FXJOMby1DOtfQTwvv1Qouvw%2BQA9IyKZhvb%2FNWrlbsa1bBEyhrB2lh2MbaHtFLNRl%2BH3nd5IzDrMOmb3gwAxcxDHnkMi4VTY64ItsggtQJ0C5DgqwT1oLw6PsF1BoqkLg3rlVmYFcZMaWjPmB7HSn7viRyECyD6uFoOJQsZ4TiL9b%2F9PKiSAWZHx%2FElkMipvKuWf%2B29mn1D0kRRaYvSf4hpycF3IvPnCPOeZRBcqF%2BOFXqRHogr7uIA9Uq0BLzAHBEiGYnLcbeIOubhtm5czsvhNcxt9J1Z3yp%2FAKaTQ0BmQtQk6Cf251s%2Fc4oSSNTCf4vEydtewmLLJ%2FhrEwvdK%2BTQOw4aeDYPqzhfzvQLR4L%2Fqb3t%2BzvvnR4kyiHN8bV6ovsZB%2FNFrgxlUSVYZn3OkHqV72W6W%2BSHnp%2B6YsLCknRTYDGLjiu5D2Jr0a54isA068omIPdeTihZdEVZVclrG1MN%2BAzEU26vpRx8umbHAkSpHpV1xhAcLPyWZ015Rqahq9vmXbwfHG56cbApOpaY1ZlyS8Pui8Fy%2FdBCUKd87zlPh6o02lssA1au2WXKtg6OnNXa%2FT9t3PJwPdPlCLjmzfx8%2F7FvXVvx9PCGw6fWFsCirh2Rl0eNjhCYg%2BTExLlQcBQIwuvVJV6GlxMsi4yQPNwIhPyjjzNGjUk5AyeTJC0NhV78TEFeyliBzJgcSubVhHr20iZVtIRYhdkfd4YOibUFY%2BoWR4Ucqx%2Bz42NrFSmIr%2Fg3xDgW1DH2O1ty8ZFdcXBcM2piGtf9VXyp%2FTXOATqvfiY5%2BSXyHDqkR3npMVY%2FjBY%2FPpu5P7HeNcEUoe6Zz5QtYEJGg9r%2BZtefiDwDujIIvCIQKoclw2z713c7cvt%2BoSiRECsoDA8pwWFI09RD1pbZKqXL3sWy2wjXK4lTUVcn335h1pUvBdGCRmv2QEbEjm9bCfMumpO9wZt5v4B2J2aKCnGPlKOkUw1SAsQOTh5qofL2qK%2BbMUCiSCLjsh0g1MTw3z0GT0ejann4nLsAjIpKlLU3bgpcE9RWa9zIeKS306xZvN5pN6lu4nWCmFxU1HkrO2ycx5C1%2FNniYAa2lXNfuuW4GlzhWt7agbvpfT9wSM8wRjyMEbE8enE%2FXNaASQn2tEGaCpLbA4T56Vi8BDbTxl7B9OM0zlOz4AVZ9ZV4rrMxBzfcq%2FxO4n40i6vDNqN5Sn9C17rNDxsz7ZxvvLPwD1864Hldo%2BMtxWpXYs5bhz2uaEXrZWYNHE6Jn6KdGm3y8UCrAZIc9P1Q5frCpLIWmCkArQa2S4HWgJUVV340CTiiuVdbBOI35ML1f3Nqembjm0aiIlCvpTBf2XP3Ek3o7RHZt30jB5V98BW0F7H4hiJAG0apu6mICsxq4J53paM%2BrFV5L7tDSpH%2BtDPPyLdqhaZ4aE9sWr23joRyxCel56yyDd4KY9jfZmTVVLYzg409lZN4YbCT%2BHVVeDUFf3jCUebv2JYr36EovffKojhUZjFZxu8r6zfnib%2FLyzdsf4%2BTNG%2BdxS0TNAHzi3%2B8MWm6Iss%2FZt7FgwerpIHAu9ILfNZ8z3XwvB%2BgmMAdV7xlcTB1ewKhO4ORq1dx23Uw9o%2F6J7WKNNJopTUeJSRnnXe0mdqCKH1dWsR5b8xWV5eX6OatGDNZVfitTDdyVyEuARHE6mCEcoKMC5v9lPZKy4WyKZa7aab2LqhhoyI8ccVxOwpXp5ECxJD6IlVs%2FSZmGpMhuU%2FYKkEXXNy4tlfcMEg3mvNyFApvXuzpA8GbKrme16tKkFmtIM582NLWNQtKBPmHQylWIKVg%2B9ao5YlT8Q4kD2br3Id22RK0K62mDqpAwY3Bk8RFYpy379hUL9TrnhAImoB4JK%2BF01p6Y0epSG8atxH7Oiv8oNoeHpfsm7eIhiWCk3lJA5kh%2FFoSzJSXC6OcBrbcJIeg26smOY9uyDAGy46IqpSRXEiLhsgHzvAfgzgFDtVcIZArGe73pudatl6UtGUcrvI10yjPH6wODbsdlPm0d3rqe6VI8wbVa22XiykhzQlKs6W63TajA9ZZYpxePBkydDVB15%2F81eykEv8XJKgV%2F6i32et4i881MaICAJ9m3kwFnsN8f5lgXjSqypr0lo0VA3TdM8%2BQQ4YkMZ%2FYKMov2rMQzNfLOQbcNu0JmVIbfspuWKCyjcKGsL0d08AsEzWYQxPfMiCBoaHATbDLxcN8kWLE2haBCNCeDdHQbbBOO%2BmF8eXwZwDwdqz7TVMI35phYbdJRPTTtGjgaT03Y6OBeez5KWRePvQgjAZkTGlNIvCDa%2FObWNLtRfwZKBAf43sQg3N0VMUtfS0%2BrOa9RWhiO8FixK%2FJc2eTfp9oImcNWUyWqhFEDXmODqwt%2BEVb0nHqnDrEyYihvS1qkINFbxmBqu8flhRteo1RMXpvnSkbRxNItrbQC8e8d9VQU2khhskhokU2LfKFe3rISYThn30Qf0aJZuQEvlASojSC5Nsf%2BqgsWPS%2FEyOsDiM%2B0NelPcidTnZzt33HSQ0qKfJjq7PgPj7Jlsh0IhDakwokLm9QFqjgQ4PZB8xl4SxhLGmgzdENdYoW84ARzc1iIpoN39pmfIcx7%2Bb0cN9Y1M852oapbW3KKBVOe2jBMBK7QYpCFCCw8%2FWf4PwtAhmTXGxQgUajZq3G8hzhk0Dn7AjvYCIjAiJXPqbgRihk5xjc52nNprXOYKlu4mtqLfBMzfPm7RdZyw40DJEVXRVHnrfY%2F1rf5DKLBbL8s6XqrjWrNNiNckOJzDYQ8Hl5bU%2B9ASfnhseiXgTmyBxYB5WAi8SMzAO%2BXdIXInr7yQjNn15tCAlG%2F6YCmVDvLNPLre%2F5i28X8R11kKUZqskSQdWeF82c25KsTpmUbw%2FFPEE9yItDVcspZyY9g6SDjvMDtxYu7QuhGzaq3gUcJ8l2MLgkgA8T6oOJ9hzusKAbnwje3MP1n3IIGpZVo5TQGUoP0qtZkzacLCtBhAwVTPbctggvnG6BwRnmIOaALT92BKehfiBQtF%2B8j9DaxWKLhB1bCh5%2Flsxh4OLq8zb6CFWn2ZI2jad5IRLGKTCt2I8wu1aHnMDBVqkhq%2FBPiLabNklAwdC6Vl4H9Y3kfiGbHlec3tP6fIZMJXU4atonAmlY%2F1jAyfnzrUhqHpLCm8mT6iaFvfBxrmnrt%2F03%2Bu6d9QYhlN1qmkXFejCVko4BO7cGBT2RaCSBDpN9e95FeS8uG7HrobO%2BrfHB6ttSt8ocEf4VPb%2FIH39pUZxYI2HlZae62%2BVqbdMwTEToPhqYoO4lameyzJDG9zScPZDZnFeO5LY6j%2FmViDaOoXQ%2B95YD9L7MN8f0G42kzjQhCguvHrO8ijUodyLZMSiS14070mAgt3MAgJwLBECVaL5%2BwV8NMPEFKIAkB5ikjAKSxGcsexIvuUArgse%2FTCigswuiwdc%2FjyuiUwDruygKFAjkNBb1mWsNCok%2BA1YktJkf2xlc7YO2O%2Fr29xAQ422qmaQKKD4RGOmxxvbQSYhtidrojydZNd4xCEi2gTdZqCpDVDhoCFfdP2qeb%2FxWNVax0%2BAi2Y%2Fg4Y6J5zxs%2FoOktutuVVbAHlDkPw1Hmi1QMizxDxlxVMhkxl3ALCsDkrQ5qe7nNSMPfteqIcvbCaZFhD%2F9ycohrsrd%2BKMND6%2F%2BOY8c%2Fo67kBLmHTCe%2BzYJWhM%2B5cQk%2Fq6BYnLhhQ1BZiKVAMkSGCeyasCZr4ChH%2FF5UyXaTLe69OQwhIvd1pm54BnbPVnW6wn%2B6LGrEIvXpynvI4dIU3nI3Nrif27JVr%2BUQCrKQoRwX%2BpHP15K6Wh%2FjNJjTu%2FvU2bFaoraH50piT0tAEysUXSBYQk8Byu7Vm0Zv%2F8smSBcxEmFQc%2BuDR7qPgPGsM51gYY6LmdYqvQEm3dkHSxIRDBdKSiWAYG5%2B9eke6zcYCn9a8fFdnjnwWr05H3yJQWNGNpJdWhc%2BMfxp6W%2BaQFICRoOnh2noufKHG7n3QeVwn0EW6OQIBOKLJSoiORVIBYHeSD3iLayi1EKZHlEVTGC1443871La7hWbCkrroFLwYNI1ckDynD47%2FbWdMedrtV5t6jsvAYw%2BCxBppnWK%2BiKKd9eSu74jScQX6uOuBWOoYo6C%2BOR0dt2nIZcbHV7wE863cIDQgtR3Qu4KrFcRn1nXF2YayS%2FedJlS3MT6maxBHgEktYipHX1qjNuiRSOseBIYg%2BkLRgVzqwTquu6zBIIXA5Zp8k9MRuLsXRzu0l8HluCQLZkjtwR00fE79kCYaSJPpJSKKeNpLzaqnmXRr1s0rSE%2B73VeoJocmH6MJMgngJl4bjOPz2J7iwL4HX3ojjxltRqTjX31rc5f0SajtxEvvqvkTz5KHAj1fUNBhee%2F9sJ0o%2Fst7ApFxedxNgzZSU%2FQUr4A3LyerY7bzs4mmJBPDtm6yc79NeKnYIGN7L480Le2cLb1ZAEPBwqM7p25Ep9YqIg%2B8TY7C%2Bljl24FPbiduBflhm1PMYV2xnz2D8uR5mym5LJzj9vEQSIX4It1AmaSayYO7T1s2BUQsuAyFzp9SzWXqcEG5UxJF%2FeuLsDe0u3Cbk66VlNPU2ltSsG2Iveic1tlDVgvWVlVM5FqrVEWnYfxvfuyyE5y3t8PG6FF5s0B9WaS03SvSPHLP4WaxUoMbSAwjQvP9zvUnCuzEVISP9G7C2CFAE%2Brv9tCib3uMbzAw1UjJ%2Bq6itv8gMLL2%2Bqj%2Fs6FakepNEOnKNot0H2TFD754%2FD5EBSJHy7UyNouLB0S9TfIDyONQlrFCedeDx1RGUuJsB56Qn0Aii1urh9dMKpToz7mEYKsxSQbbpWUjIQ3O9idKNH%2F6lgwFef0es%2BgT6GegoRDcTTM6hQR%2BX%2F9AwSoFDP1yRjAAbNonTxXkyn7ap516Wn8oLK5%2BgQFZHQSP2uGUtOH%2BlkcGcx1JiA20eDssWOTkT6KOjjdAEz%2FutnXlcjK8823Ym21oOdobYqsh5%2Bv2%2BgDvhUCWs8r9P5bdrOBndCbFp7tiCjMKCylQy1%2F2H2%2B2wUjU5QvYk6gCTl%2B3ru3i55KiQ6rlBxLS9kejvqGjlcRmyljqxExi%2FwCVJmqKyfRckUK%2FtoCqLWlJIHHMzWgOBCQDu735Na%2Fi4W%2BPTzgDAYOakBKPbISOE9kQ2%2Bv0sswdfA3b50MIZS93Pz0%2BxOQhef83CiK4wu9mdd6HoSXRQcxAzztlQ6qB61A8zior5Y2p5DYGx8zWbUAYrYX2SRlsHGFnm6GApFDs%2FGTrr4oBKERyBOd4VfSC8zYuL1MqIwbLkWqrvG0xU3Qskohb1bh5Thlt2tTIMYiNrxg3GZJ2G%2FG%2F1L7B1UI%2FXS4fW3TcKLTrqBw4GXcJWaGi5%2F8MBgo3q8330xAmgaLxFPWnm8S83XrxpYnbyVmVUsJHyXfRtjmG44x6eNlO0idIKaXohXTpKCP0VV%2BcEujZynHvbC0Yerwdfm3202QSRc3iIyD%2BeTWFSJ%2FUoO38pcWQJ1P%2B5QGTe9k5yfNVCT9cLtm5j6cR%2FmLZfD3QjJgsIU1rTTq48OFymwJKMcf8uVtcQnna9AxN8xf6wkqsz2uRLQnBogjxC%2FRUujy8Rl%2F0BIQW6UcxO7yKxiVRNnHJYAi%2B7Oaag3cw4qkO5O8a4OmKWcfEhuEE8Pg3gsi0kdERqACqvV%2BKPspfJxmQuJHbAxvK%2Fi0QyTTZtBZTJ%2FEPgYHlncKiOITeMjwAXY3ziP8HBsRhMwJD2IZVTdpiJl7mpAabiqvwa%2B9pcKwOS4VpY7Iwq%2BKX3RHvLk%2BTJAusS3D6MURKkw7aGIe7z35OtgtCLi4bkacwZ%2FxaXQrqSfxoZ0kEPGQhxk%2FkkMIwe800crznfAT3iGHkWn4ggwqWzJPdjbMnB39EbdyPlZPJlv15H7lQrTKd99hz8PhiCRqRQwepkst4J05BH0Slb75MC3BJwmPkMo%2BJWsXo42vgpyJpIryQUxap%2FVNpcOHh%2B6%2Fdoiv44v%2BZshc9xNI3bu3ZTFyNHMeZHde1m%2Be2U43i%2FjXAG4hZWEb4Cd90B7htFXBcTfZ2T8OOHU5DXPLD%2BxYLnPm10qvRJWi8Ipzhbon%2FlrjjO0mRL0YD6iFSji%2FGLUXD3n6LYbMdf0%2FIOAdxsTPx%2BUEJaSYRyMjsPpbdUb8MwVM97amjv6G69tHYDzs8McIxckhSTlPMeLL7PGIPSNvCuaX0pkUNyQMwqTKaRsyD32E1bw7ZjhIaACj0fn%2B9lQAL1UhYiwZndHJjVGWy3JXZMdQ7lZ7qGxXnT%2BUfYBiSqcPVgmFy5SrXU%2ByuDkpZj9%2FcdNUGj9kf1diCY9LCA7wBlCLelGuOpkdwVMdw7OTbp6f9qjSJ11PXEhWHV4Cj%2Blq3D20ZAM9VSNH2JbgsXNQ8VrPdaGF9SnEhsdv%2B97IXfwfxSBOGwG%2BHiaelq%2FW0msBdXYwT8cKsxS6j9whby0As085kdJZSTRcLywf2FZ8IFrodjug53%2F07h3LRPcREWKSmTl3W3HPB%2BDj0ckMAximHfUnegOwg%2FzaUegcKbs9nGSlSo1yBcH8T9kJuvTUYEflkj8EX3%2F8Wq0%2Ffc97R0esE0Db10sEj9SQgEaHQIhGrnaRO3KjbZ%2Bu%2FnvW5aEYCRq9bkILdZYzj43uw2b7dHLKnNT6SSnUnd%2BkRxzAB8De2Ks6OK0mFHT0tkd9wGMl8ff4AJY6VWHTsUoZtZtlCSJgISDODyiEavHPr9YlvyVI6HMp7MhsHxr3b6GM%2BwyjwoKEJFMa6T%2For8xlSbwUjoxrc8NdJEDxC%2F3JAjD55%2BVMgulI1M8YCW%2FThxStokRdsJ22%2BYtVl0SXh0EL6OBDy%2BgKqzB8ygsEIFFVp7XqCGXGio%2F0P2SzNmQNSHm96RDo1rOxm%2Fo8MC8RBMAB7nXSOkkShKcTDTpzYCB5pRtokLvyZPeerTzi81W3q3I4MCnHtArU2iFXt2op0ELuWQBFh%2Fp8iuwJpWGoKjK3cmb8dUJ9%2BYZf5XKUI3GeODWtkTHfOqFTZx6FF%2FufH%2BOqdC%2Fj%2FzznG%2F1P60ADLNeViRsRKhdq8BZmnB0qE1r9%2Fx6qtZraR9meGCIkcesDYZAPWwdJxapvuGKQV7Ogu7Cs1jHNngtF9ajvCJ%2BXS3Wx6U3bsuOaOddNZmewBJrr%2FlDZN7DJHoHchDvokIn%2FEQ9KCrP9D9z4Z9UuAWQeJNxSHgUv2OtEskVDca%2FpIDNfZHqDBaGhRuudhk6zflRDKYGgKAoVsL1z7I10dftncLLFJghud63BmWy4WLfRT4LR%2BEBnALfCWU9EUKkpd4H2l7cm8BAIYkYu14fy8MVTVHHp25prVg8wZsleI%2Fpy6Oq%2BTzqYghqwiwlVUqeA%2Fr6suh7z5%2BYPTHnVRp7uX%2Fr2w9YQuP2qWBj9ERz2MyDmR1xSp%2BqOrFCxSvCC5hpkHLbeTNeR0Tt90vQMpr0vFmF%2Burt8xkO%2BOinJ3FlVugB1TQxuLoEv%2BLUM6QHjuCvdNrZGuBObFCX7tB75OcHcw%2BQFarODLjrXYH4UeY118OKhrG3LTG1MYflwuyR%2FwVgZcQ0W6or57FbPhEoDn9HSgJ3HoiBgNFoAdg7i4AunVeP%2FQumBV5wMXCENJLIilh9w%2BlnnKAwfFIzFs%2BLG%2FNicmmP4nEOoFoeIXiCTMUuDW0350Ezdutvt9H7G9L%2BvWK6sCxCWH%2F52NbZi57XMAQ3zGz8w6nYtI8w6WUiAMuOVT4qgJcjvmMC4aCWC9KOQmsXtuxzQ6XJm2nx%2Bo%2BrctO2jeXAkkfwxY47COK1V1ihmwmbP0zBJ7JAKgFbsvFJcCy9d0hZdcYVVF1aYlB7CAnBBsn19acfAstbB0%2FYSlp2zupoN3FDEJW9fk4NlMXbnK%2BYql4uW0uSNM%2F2BXzWfGwOsvBv2Fw%2FGSS8y4JBZSBbN%2BwWsV8tRuxExS4APAYD1JVFhnCrm5eL7y2I9E7N60jurn1UC5SikViDgg6oCzIkfIgfm%2B%2FbeuylIchKf%2BMcLo8eICAeGZQtD%2FWo8qHflsszMeBFP%2FY9gEFTXtzdrvL9PQfYT3O4lx3ZuQykrEQLoiNM0PP3SW%2FRmZP%2FLPMjsqDpOgCxSp%2BuAmttPDxkTxf%2FP7VCOoPO5MzcLjTNwAluCp4SXb5ZMyC3SDMb6mCsc7Dn2%2ByrlhD2Wh90ADu3jcps8li28KPXtFR8rj5fnVaxDGjIYaEPzq%2FXo9exbOg8zIJk6VX4JcER9qbZjt%2B3xdvZkNiO7sJn9N5z6PrWoKfICESWt6m1cKH69h%2BDAIQfpD9yWYhYT36qA59YRdmIG5ik88SkVn3EiIwnu1Suyosxsv5rsawRwkLe9%2Bcsx3TF7%2F4V6IKcUHDDFM70%2B6VQ3XDZBsC6qjnsF%2FBqTw9yS89Ia81YdTHZZPsjzJz%2BiP2Sphb11%2BR6Y5%2FZboiqtjUSHxiEHHEgf2ixwls1PFSnnFLq5yTShpZr%2F6pbeCwjpgjFpg4jLePdxAHI96bMkr3tdFGK6ji6rQidXnBaAIYDjKr3%2BCNxYnN574TFNV8JsyJFIpBf2pWwplIAWPLTfBcdUPXDpDijfMi7QxsVnSjaCfFYJHHunX%2Bvhv4xYC7eCUX34kDBjO%2Fod3jtj%2FidoKlFppiVykmPvFxoBgNHi7ElFUgqeHC46xXbRdjhlXuPKKGbcgSA0RbKQ7A7%2BSttlmDBUBbGxDpK7DBEWbnbfWoH%2F%2FIBSGpnwBv3xHdXCKcoDBNl0iglRBhmBqWmx9aPO%2BL8u6ZOp9fyPrtTZglwWVpCI0b9pBQ5jDPjuPu0tf512fRmEop2hORhEqTyHjQ%2BoULShXt4ITEA67%2F75PNndm1rlo3cNUcY7tfFT66tklQiq16Uc9M24HTEiIxDOTQrituaXPHvoJ66vch9d%2BUAl5CY3X6GsWaoCWcLM3tOOTg%2BTQwpyHhPW9xFHwiHnK5z7GXzaxT6Sk5Y0AI7bHZH8KIFdwO%2FRqC11npiYJH7oXANfIeaxee%2F48GcYJ2oXbwUCD6Lr4dnRkiAHWkI%2FVHVjBJ5TpRcLg%2FMeG9Uh3%2BbMBZJAPbGHRGXzdTgOKCX0kW8%2FCrFwP2JwhJAgZ7qjGR00Ww0qdtDOK8nQaTPp1ZIoaHUGe%2F8nujl5NBeUS9ANcsKDT98nygR48kxKdHZ3WkqBj7AWr2hh89nTMo%2B8BuPr9o86g531obCwy6wnciSU7eTw3lUHC3272J%2Fgawxvh9FP88VtvF7MCY5u7vWxql%2BnBUI%2BmlcSIGLfim%2Bec6SRd%2F9fnQHDPmc1ZYcg9quwC%2BbUy26V6Zdcsv3dVMjbrTxN30VyqC1gK7JoNbnq%2B73RwI43KBUGxhAbY7lLW5RjvSwrEljHCoMAGXSqxOgXV7GeoyL4vHUTzVmXlK3S%2FTUkrUwWt3wt4FvCRRmCzJLprNArQL75eAOC%2FHZIGX5LjjH7DHflGnzOiOid2Ui8moRy0UaDJ0HOSEf50euaVQf3Atp6zcvRRRCifX3tHGmHT2urUHqq638QCSjuPcviVYS6oMN1yBS7s5IGa7DLbq8rqWVYYqqTqIfosQfZFSOhr5CpTdeKQeGuF8hKvvIT9lQyeYzTMgY4eFFF6t6i9LWWaHkZPQ2F3QDR2NRkCVgz1wt%2FG7l%2FRo%2FZqDOTwGQ%2Bs3fLCidGFfgHpQbtEX5xzUpNsZv2AoGacSc43NMYQ9C%2BaFRR9ckKzM6luq3kmNM8xgJshaauzklKkqcoQvJiyz3NiD5ZdHnt9Gd9EFGmUXiYCA19xoUWokCqi%2BWI304zF1uGVqgimASvplCh9Xx7M4yHQjt4pJMURV%2FDsNtFyVOvhb1sTyynj468NCeiLOXtrDohSyBh7zls7Adb1Q2rSY5ZL6ToJZLSyDqAIQuN1TZAdHdX8AGzt7wQuT8upi31MQYJMk3fcqb50WVN8lcuSi0UnMmCahguoWWEXwRRNyKIHScFz5uMHWDxmEdpiUlPbB0moBsxOsio8yGxAq59gUbIfRASJbcaruQi5ZDedxhqBf3gOugXkGInqgGxD7MKZU5E9c1kTpSfCUQuu%2FdTJMf%2FzNmxZu1KrfOE085Fvk16LySM%2F%2BRRwumOYygQNLRalSqBVjrJT6VKKqFOdfJXm5xpe2891TIa0D6kXW%2BLtUkPTJUfILU6IBT1tHnSPiV29EGefI4XtLRihsgNxQMN%2B%2BhzPAgZgT%2BWVGKKJN8BU3VAvY2RKXmOBtqp5Aieel3OLRNE3JUaYc3FDtK8oTb%2B1dnOlX2Do7AMxyIF6wFhE%2BD5QBe0RT%2BRvkGpeU8iq1tUaX93Zx5vrd7%2BoaTz0eWQYPxD7FYlJnMKwp40H6NNVvKjxX4vm7RqXhpBC3nS1bS3TNtXg7MUr7%2FL9jruMY4fqTgLNl0nL1ifbc25tfzJmPFnrxbGSRF21%2BadVReIw9if5ANGixw4RSVd1Ro9MdS%2B3KerxTMKWbZYNF%2BzjYKoBRfP2qpc6pdEa6LaEcTkqhWFO6PQ8%2FEZUf2VkhJquhuKtuPhwqak59KKbUEQKJZX5kmvGbz8aCOFHaP2sEawIEM81yBiQQeb5avn8R%2BQs0aE9gpnR2ZGXSxcxgivhJ%2B9ATMEq4azBZBditmSRoEyyRocP2JeeAAq9K%2BcVwTT2zQlKLkDKx5i2Jxd5sQ67yALz09XxZHozcRMI98gb1xzAvPKNRjp26iehXaUSTl%2BOFBlwUMR9Nqutiyt3GDjT2bStSUQuI64Hn90eaVB6whCgKTGuYbDrdmOUiEkQX9Nb%2Fs5umWkvxE60dL6SUGFM%2FR8G%2FoxJKH%2BoB9CczmKg2WpMf69%2BHwzcRZqpE%2BJTaRL5cnYUEP5WGR8%2B123O%2BVLfmO2cLRysOidDr56IjelCiIgq9nZGyfkMpvLv0hpkEcjerQJpFXGKllFBILGnMQMxWiOcYpxUiDzGfoufwInI%2Fca6Ag5EA7FQCdbrI0g7dqtUAUVESMA6PamSQ4HbkLD32ymfldg0sDXJjjSvnpFBR%2B4I4YyTN7SjtXDOYzop2Dm6%2BYljrJMTDIOLkc3SQL3w48SNE2HwrdkMKTfktTdLk1YdnMmE1KrgbW0DzrD6cRsuxAoJvph7tCaQYV5YZ7dbqgVxclzbNtPvXPWxOe8wK3DADhbyHctb2mp8aQSAdsh8uYIJOaE4tM4visnZgECgzD%2F%2B0j5Y8fQkMWPPnDQ8UQvOKgHzXpbfOGtQk%2F%2B6P2F%2BTrSlW1DrAhDjRnApx66mk4iPmu62OlJ2Pn%2F1vvwKcK9eGQRN69vUfGmhSiPfIAyfYY9jPsETzOVacvQNU0sWu457uc4EJ2ZRK%2FadP%2BUJBpcz%2F2GZpqFYwaMTXXzNqBEzI%2BIFPue43lk8zODPAwKAXBqXHA22GdmiWiOEP6rfbhE6BYll7sXThRjKKvre9wjtLTu7DcUPoNmmA8pe242JHbOW7Y%2B6Cr%2FXJEXwOeX%2FL6%2FLHaYJNApXzIDZZwEbkQQOk%2FR1cuI1XPgj2a67uJrcy%2FoCw8UHqjEXfW9fQA3h4eCttsbNmBKg0Q4uTpET7%2Bfobqfhq11HThGUhmC0%2BN25UaaauyeJTD5hmgI0IuNOdDtuclwRKjcY00Kp3QB%2FWUTprYDrgGvET1q5Gb%2FeH3czQ3TFgNGaSootOPzkqZbd8eRCBIVVXZByBN9GjPl2YjwDUCEymYeBXG%2FssOYRMNa%2FhWgWaiwcTdhSSHnTsLCtJdLpTCCkkfeFWgJAU0NUmzB6hQgdMtWPaJQho1fnhawpmJar2Z62pRv3nOBacqaLxPL6hJa6A%2Ff3oYZFxo2xv%2FpWN5daWVoNWOpkpmsUmUEoe6WuX%2FQWiQ9KpoT9vtav27Fh1ztrvXHbPmLsHz7%2F5W90tySebWYCT2XUi%2BRpk6PXCrtY2byC9RaRLGMHRP96LXdZv38n4Sr978ExBtMJE1U00PoxoXy6kz9ZIYLMRVgRaJDkm36z9A8S8%2BIEPTvB98ha2h7hh8cmQoUkAtITGqEPTyBWJCH0nbXIr3hsIx8Ai8DqeQLY17EJP6p0ETZYzv%2FzE1YVJCKwaGxysLfefSz7IZFvYn81xqwjQjZa%2B4XatDctPGnkvaW2ZuE6aI0d%2FxfaVkVIv45DV4f3rS0QjYwNPRqoiCL3XRX38x1FsE5GMCipXrXMrCvSqY9gXosuE4MxiY1dT%2BtEfAo9uYTrW9rU%2B6pyO1wwubiI%2B%2BuFn%2B%2F8JQe4w46AsjBJ5pjvph2I59Xh7VtyggvTEyQWUsmXpBs9x9jG8GFWrAz0eO9VZ0YS%2Fn1xXDQHvSnmJSiHYPJTP8J5qqKRgx8LutxwTyri19%2BM%2Fu3GvrLlqsvRBBNVqSJ7oKyuOlpLShMFQxtaAYWBRYEtgfb4OfoF4A%2BWO4tLTX7veOUCbpX%2FFVXB%2FhBriYqk7j68G0LdNfhgs%2BTdfoKM%2B7yK8AvQ4yCkjSxrCoERvpkLAO5M%2FKkL11LRnX7xZ0m9iue1J7tRK6E5QnaqrSUsYAZMSOhiZ1Ll1ylXkVupQwn0d9vn%2B3I9bbWkCw9AQR%2BeImePcef3pjP9vqiT7CVdpU26sBFUDZheapYaUPQ5YMwRyQHRabQwv7K%2BSVYxF9OCbIZLTVykqQDYMTd9XULMfrmkxnYreGtOA4fXVA9BylkIGjPIw4Sbz4K1iNuoQoWndpAdrHiB1TAlpjh7%2FvmSCwdkmAFq2Ou5Wpjby6uI6INSrkFlKS%2FquEQojiVc%2FWr3FWWxN2h9y0Cyx%2BFIgynmb0bXMvFiYea8DK5D4qaFAM4O0iCgCSHnP0rjyjp9ZXe5WjddxKioZUQoKQD6WhwycjzjQnyAoLU%2FIvndUGjx5SouzBbnp09rbRUpvraHE2Jye5tGopeYJi4OaO38Md41P0UAVyXZqDb4yQIRBi2lOJ24iyeiJzlcz0szdS1YtXULNmUXx%2F3tERalYbvy324y4ret%2BSCr%2Fvpn1nIevbkcQmE21dDmM%2B3yfs%2BLXhCFIJpqAWlx0yUBz6VZ0ideA1bq%2FuXX%2BZa3IVu%2BKCQcK8KQoq13xuv98UB9RkHidYSB%2Ff%2Fno6H3RDZk8RGcrB%2Bx9TgDL%2B58KMVF62dEu4%2F00CCuWiHTEFiDWQeLJYqDpOyBqe2JEzCazm4bG2QzFUVaP9%2B%2FN52cARQ07T9RTrk1l5iL%2F2rsffEdeQBEzsju%2FZ6QsUK4xa1g%3D&__VIEWSTATEGENERATOR=59A5EC9F&__SCROLLPOSITIONX=0&__SCROLLPOSITIONY=0&__EVENTVALIDATION=3jHC%2FbS0pQ6Bj6Tvz5Z4ReGoVJcUE%2ByUIiZs8TAW1cmbV4cNj96I2%2F0LoFoAsAjhErw7ioOegcP3%2BAzMm8x9wATY0sHGOl8PJmAnZ4hcOCA8U5v07s4vGrVwqt7aSYKH3TpdSFBWPXWaab%2FL4oz1Qd51HhXqabKVs1SCAAtkWkBfcFSiBy%2FNeOXhcPnQCGpo6kndKF5ZUKu%2BzbuYf23GeGYwhXYSw3dQTkklpC9sJy5nL12KJdlyjW4VrzF%2FPvGY0gB%2BIbdoVI1NTFeFFvX5EZ528NSs4rnyNohutkHzP%2Fk9Z8HFZEjzk7ErA4CkSNePiIbi4zxuC3n8eXzXYPUDTxdMpnzVtPf36wFqwaAzvEP7Bpg%2FQJjD9RnvCKlPdfVZx%2BHzRkhwEyn4MHVhea2dUBCJTMCJgCVElZJPTivXYM925GJxlDCVzSD6UVmmL%2BwsgOlLPhF5RO9xuPiC0yZvuM1FveyGCUSuxVRggk5Lk2CVuJ6kpqhCPIa5etSVn10lkSu2AUuUd1wAcUi%2FNb3ZZ2eCCn6wpVQrHqv7ALP%2FGTRV%2BGaH7tt3ZQHZ%2FQGu2cfJwb5rw0zbIrv7ATJ4VEl8z3K3DKKC%2BwbcUeTFPSMkPenamWNX6T2w35whBBmkShrzk8TKLku4u5QezTFJrMxEY08WqJ3E6L34J9byJmNlb6oTJ6cVXhSbsUqPPyqr3%2BXoAcVOWC1C3CdX%2FNlcehWlF4fTVQBqyAAN3kQTweXO7SyhhX4Bp9bTw1DEb8dVSx4rqLnw3NCO1WwRqAFn%2FlGWN3p0Q74tevkPpkOD%2BHCO%2B2t8Xq3qGYzPQ0ErZKEwVWJe66cycX0fxB89Ec4pqck4mAE9HUksisSt691cW9s%2BZ4KqlGwVyup1d4V1KIiXJohdX8x6%2F2gxbvKLIR%2Bms%2FJnN4%2BwSMbycAzSnZ4xxUu7A7Mru4CHeiaZ0u2CHt46sG%2BEwt6uCzaW5XhMaXddkjaMeFgj4BDhHgumSAFWmkTXnkXWLPm9wwNkFOsKJw6HN9BCxk%2FpV1qc35DjJV0AN0MiP8jUErdW%2BCvRf9pJKL7Kasy3Ib5%2FSaFnpAFz4U1ure%2BbYa%2B9%2Ff2b10hVw7CMXwCxCtnnjDCRy3mWIN02SXLbDiepbQHmIZ8tAQ652nZyNbfh8uLsgaljTUeQvpSgJfXrmCW%2BwD3mnYopw4ZoRlwBFq7uPK4dR%2FSIPRgEl5jqEuQlthFTcYdVrjQdz03WQzUasofL87HvawLszfbWux57axMUyaP%2BK9eKkDyPX9P6tUmBFfki9wS5UP4l%2FGojAesHk0utOFNnRNPhxuoxdyRjG1K18tzcMQYxZ1GY1p3Rw482nUsJanHodjDKn%2F6uwTeGuHt75RGZXb%2FTY4%2FQ8X9iKqw%2BmF2BGvgDRvxq4wS3sEPdpR5Wp6VGhvgKL%2BRRRhNBex0xf9bPrurIsxEDYq%2Bo0Q11taFdRZLEUxA6fCg600rGzziIkciioXfNmfXi%2FU3vsh1T6qk%2BP6LkZT%2Ft04Xfz%2FTruA0Ca7PvM3e7vl2sK5wejrAkpvkmhXmjdP0kJdbwxkWyKP7jWMUDr%2FiyaZXJCTPUc7h%2BS5d1hXSJUvQAmJeDJVEwzN55i0rle9gAtIWh5aqcvHMrlqVFGxwNXACe1myorvdtQmad3bwnYG2cpP2fUKGM4XNoxUmK2pg1rwclz16i7%2B2bg5ADQ5N9XKXJfmgAQzgoEyCgIcgVEvHzkGgTPcoQR6Q%2B7g9j1YDINzvoO2mz26G4sGK2oUIu5FBFoCD1E9htPI6ZlgpJ9VQoLU4zFXGUzvytAco4pzGgBvrI0xcUrBnw8weIPVdm6t8%2FtamB1IM2gyfMqOu%2BubeuAylqcwxr4XgCCbSEPKocPJ5np8Uw%2F7ZkMZPWOeu06hNNsWTqv18n%2BMOz%2BQgshhLreH%2B6J5J%2F6UVEZub1lVM3M0E4EEGirn0W59DQ8%2F7xhx6qOUMyqieswciketcopG6fuuuylurYO9bae%2FiQrUDcgoAvEr5wkam%2B%2F4I4J1Ou4eEdUCBuZB598gi8tybvpMGRHEtQblnwNfQapGpZnLC3DCBfai5QNHJM1VLAimEnklaxlkCN82L3kBN21TKLU8bmywaUI%2FxB4Pz0p%2F4vQaK3yeQHQpmjmWZtIflSyIcney7dt0V6zIeJCWQcXePP%2BymZ5jolGdoSX6n7s89Am939tvXEqmMFt0eE6jDg858VTr8fHvA5lezl703M2WgsNPzQ%2FxM3bv5wKSYWze602JpLxIdL9yKWQESqR0eF2maRT5MLPEilOrm7jh2YBJO2VjVS6KQg8h6mxLYyLfKAWdhgb9oacSaT%2BYJ%2BnU0gYWXgaXkWEqI0IB6BDlfKTiJgKN2%2Bvu8vT8SBGvwgYDK1%2BtANWyHw9uC%2Fo8VVQm5RLCYN3upXDZ9d3K2WnAEGIKQqCm7omSkgrAtnzNe%2FICXcpriy5%2FWBg74%2FjAyX%2FJI0Y6Zm1xaS1eHZ0oo%2BNer3%2BQP0L2fJaUopFG8y6YToQDQSCrFvcgVsi8jAanO6Wv3X3siqFdGTGJkeyKzDegmmqMVBk8n%2BIA3kUa469QDJY%2FMpy8Yb5MuS%2F9MxbdiFARr97627yfVPPWvLo1plrYNp%2FZdbftCCq1gpXPMQDU1fI6qLhblQIrlA9rfhgPStGKMN5dDd4xQM9aLMTzCxYryztLJlYlBtNKcXVmmfbRq2y83IyRMI7TmQW%2BdEtFGEuecfr%2F7gdvPIe0boPb%2B4s5eP1nl3WEX9lVL5cb5nKnSnbfJ7SrSk7oqyWtFbWgPHBP74XrD%2FMC%2BY1me3Pu0sUbX3AyGCWQuHHuZuLNzpsVVe7YxgFGhumMP%2BdETZk44t499yzjeIzuBNDbCwgeRgw5xMHdsdaeGGIAxZUvuylFNh1%2BgWuUPBCdZZXQAGiggyd2jkhoklYvxeCcDkpbTIu%2FJLVum0m112neF6U99R4mbjb3shjAfAEDxZGzq%2Fjzh5OXrq0gxUr9kqHBXeiNoFOFbb3UPoPT6YiTH0uAiz3zt1zcZwsIPfYQvCt6lR0yo%2B24p0D%2Bu0wA1U%2BIZIwcJXRILwYNlhc%2BC2lnJtS%2FifVZO%2FTcG0OqC2x%2FwrwcVQnzmkSypEAmjaHmkNB2uvsRJsOxOL0HcM4wTU16ycn8BsO7cegdIB1FtVqdJQaLEyI2u3tY2yoo4WPSZokhCCYXJhxMrZhTZFjFn%2B1gOSX%2B%2BOnuoKRzUCIIz2RhW4sJRJxJZUJVnkKdrY8BxXsCxKnSezY5q%2FN433tpdmEWvBri5glqDQy8QD9JTLOP8FS38UNebOVpCCbRd8w2h5IEM%2BqOo2A0Mp5ysVCjCbMqqi1Os5IZD4pfZYgE48Tq5xxygzRQNsf2prrRS7lim0GxzG4XQk2QvaPyDIyKi8wUC8H2GyHZtIoRgeC7BTZeCBxv8pTIw6%2B7sk44YSEiIZS3ZOwnQ0hUlCrPQyeYAoxXUXQRBD9HSGI3u6q%2FITVCWNGNuVMeZCF%2FEazroqLALWtTNmSjp9KvE8VAddozsfxPWDS8LXfKpYzVRbvUTSU0nRv6BF6Damqyl4Khcniozctyy6NV4BoX38XKnzZopIEcSsiLOnW9hcJlnLG0z45G%2FIo509hEEtUIKBbig8Xzrpc95Bkx%2FK&__VIEWSTATEENCRYPTED=&__ASYNCPOST=true&'

new_data = get_new_data(response.text)

result = extract_viewstate_value(new_data)
eval = extract_ev_value(new_data)

view_state_encoded = urllib.parse.quote_plus(result)
even_id_encoded = urllib.parse.quote_plus(eval)


# print(even_id_encoded)
# First update VIEWSTATE block
updated_data = re.sub(
    r'__VIEWSTATE=.*?&__VIEWSTATEGENERATOR',
    f'__VIEWSTATE={view_state_encoded}&__VIEWSTATEGENERATOR',
    data
)

# Then update EVENTVALIDATION block
updated_data = re.sub(
    r'__EVENTVALIDATION=.*?&__VIEWSTATEENCRYPTED',
    f'__EVENTVALIDATION={even_id_encoded}&__VIEWSTATEENCRYPTED',
    updated_data
)
response = session.post('https://epanjiyan.rajasthan.gov.in/e-search-page.aspx', cookies=cookies, headers=headers, data=updated_data,   allow_redirects=True)

with open("e_search_page_rural_new11.html", "w", encoding="utf-8") as file:
                 file.write(response.text)
