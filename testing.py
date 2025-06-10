import re
import time
import pandas as pd
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from pymongo import MongoClient

df = pd.read_csv('Check_Data_F.csv')
con = MongoClient("mongodb://localhost:27017/")

#-----------create db and collection-----------------------------
if 'Epanjiyan' not in con.list_database_names():
    print("Database 'Epanjiyan' does not exist, creating it now.")
    con['Epanjiyan']
    input_table = con['Epanjiyan']['Input']
    if input_table.count_documents({}) == 0:
        print("Collection 'Input' does not exist, creating it now.")
    data = df.to_dict(orient='records')
    input_table.insert_many(data)

    print("Data successfully imported to MongoDB!")
else:
    input_table = con['Epanjiyan']['Input']

output_table = con['Epanjiyan']['Output_Data']


def fetch_data(document):
    district_id = document['District_id']
    district_name = document['District_name']

    tehsil_id = document['tehsil_id']
    tehsil_name = document['tehsil_name']

    sro_id = document['sro_id']
    sro_name = document['sro_name']

    document_id = 17
    document_name = 'Sale Deed'
    document_num = 10

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://epanjiyan.rajasthan.gov.in',
        'Referer': 'https://epanjiyan.rajasthan.gov.in/e-search-page.aspx',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'X-MicrosoftAjax': 'Delta=true',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': 'ASP.NET_SessionId=fidekpr3koysgampm4f0vqow',
    }

    data = 'ctl00%24ScriptManager1=ctl00%24upContent%7Cctl00%24ContentPlaceHolder1%24gridsummary&ScriptManager1_HiddenField=&ctl00%24ContentPlaceHolder1%24a=rbtrural&ctl00%24ContentPlaceHolder1%24ddlDistrict=1&ctl00%24ContentPlaceHolder1%24ddlTehsil=1&ctl00%24ContentPlaceHolder1%24ddlSRO=1&ctl00%24ContentPlaceHolder1%24ddlcolony=-Select-&ctl00%24ContentPlaceHolder1%24ddldocument=17&ctl00%24ContentPlaceHolder1%24txtexcutent=&ctl00%24ContentPlaceHolder1%24txtclaiment=10&ctl00%24ContentPlaceHolder1%24txtexecutentadd=&ctl00%24ContentPlaceHolder1%24txtprprtyadd=&ctl00%24ContentPlaceHolder1%24txtimgcode=&ctl00%24hdnCSRF=&__EVENTTARGET=ctl00%24ContentPlaceHolder1%24gridsummary&__EVENTARGUMENT=Page%241&__LASTFOCUS=&__VIEWSTATE=jga49n8%2BalFtY%2BPlXlRB%2BPdEBC9k3Ag8rbceZ6xMEoDwhRE5kqYIVpmjfwP0EoxZVXtspCkRJpjqcg9%2F8jHwyJ2tSLMzSMNqfVYs7DvIwF5fG9ezoE3Cmxu862q7UKwxgoEDuDBO92e6R%2BIXzO8YtB%2FH0fujTXGT9xlUtOqxJSSkfmm77fw%2FoZw4gYSOD3KFKWktry3Q38x%2Bs0sJnE3YNkKj5P02kV%2FP0b3i0bKzSAdjyVu6WR2CjZ4NVkl4bWdmJm6pWy2D1TSLGLL0iCEq19r0GXr7w77yNQ8cVpn%2Fk1i%2B3xUaBpf00Ga4FHx38LP7XD7aLQGOp1iZuYLMTgI1DhJVGNDRnWLJGbzWxJxxknqRieacsMn5rVLj0dRKTlzWLcbC1h4z34jYxdqau1nGxNHzatUyqAwl6nqrxgBRe5%2BSwEcBaI%2F0W6gjS16rWhSPBDPMwIzYYCfnvSDF6XXiXFkT7daMd%2Fm4tFo5P08pb9B0kawvJn3ogbGfi8REUF1W5ynJn%2BKLIQwcrtJKevigPYIyx63sLGt0FRPR%2FIgv%2BapNLKgb2Orr%2F8Gg6mwtjRH7ozGCa94KaBJpTsO2zUN4eUuDzj508cnQNl8oz2kKdd%2FzdB%2FhCj2vz%2FEDA6rudXrZ%2BEHSlpGW2Ykdm8wIov3SiYyMXkhs7EV4rl4RGAuV5TtM9KRS6km7%2FjctIzMm0aTdu53IMtJt3uimWJKrVcamksbLEDYKcfHp0Mvk8TjKfX1x4hFSlpKxVbdYCbm7AqD3VD6uqtkHADvQ3MnqgEk1q3vgVomVoBnRFX5ifRtm%2FZpoMW0HEHPHHRNxjntL0RiwaOfTjTXPdTOQbohKfG%2BdNx%2Bfa0sSkRCCbk0LW7KJVq6CZDgGgIVh5BQoBAq0MvNRYx0a0pEH5pFwhZNIhBLzTT6p7f3RVOeNAkwC9iyFEhHNQZqeDm6Li%2BxckEzm9jmbItbRFAR3R23F8Exjeu0%2FMMh%2FmCKgFNSUptbG5yOh6n23WGnKEi6s3XQz%2BdQnL5%2Bbdr0ObjbnOyrdx08BmApfSbEhtxdCh14fPEUIQLDxV694h3%2BDIyhGSfxLRtvGF6b%2BvCNvwj6fLaZoOh8KQ9JByW5tAw8dS87XGLoCZjo%2F17gFMgp1yWbGbrLkxEVWFO1WX5Ue8h9DydXAp9TARF6%2FFP121w6c6v%2FHBzG0u5iOekHI87WgMbzV7ePYm%2BWiGTNk9ZrFhn8lPFnAB%2FHZoGSO3tPc9v2A%2FMUwBr%2Fa1k1eUoj1iZWHjEYn87Ml8uHuJFP7EyUjzX7wcaeI8dEaUxS1anP9DyQ1iUHTAJgVvTt0U8%2BKoW%2Fl30mxr8hNWapdwoPnWBHWJaYchtP3%2BugkT%2BmAgvXma5Ytc2OAjBvptVPo0YmVzXAZg3y2uCRC6UH1OVJPc93sBpEAtUR0SNo15vUPr%2FGEPAHtZ1poqTo41NVC5VNr%2BF3TjXYNwfLMZLc8TMSF45lD%2Fki1wye%2FLX7A%2FOqb1vGYiy3PvrIk07lAxZOmFpyn15ngG3N1hxFHDz2wLCXFed30CZ0lVoPM9%2F6TYiC3GYE98btUdGxCmSCO6ncmNW0K5I5fEca7%2Bi3xr5DlIiO5Rl0bYH27YpwKyQKvJUvCOaGE9qmoqCuFXnUPxHNUbgCvP4k14kxXBCMiP2G6rMXwVTyOy7LDt7lrN%2BOyVUHE99A0Vi7jNTxTnO%2FiszDdY4abOj6rbJhLBbxruqguo6DpAXXUhHOSSBP8My3Qidmx7fLkw9qol6yvCUqaKxIeEM4xuPdNzzNoCBgGA96lMhC%2FW%2BYht3t7FnHJMi7PyzJ0h8XkYw5p%2FSx6cLR6ondlsfXUmToF3RJWiU9n6M0GV2rKrUbleQtqj27KwZwsGBGPyC9NPH3h3NB%2BEKQR3zJGU1XbPnqLcD5q8mi0sEbulH661Uk7X7R637jSzJ4UDlOPfyrT1etorpZHVJCEJc9nVct6g9%2Bqs8gxcXyItP1YyByvT76Vn239KQRN8ij3yALsMm8I9C40wqkTIRbR2peioongYCbhfZ00LwUTu56Px%2B6TvfgOBrigM957yFkkbZojKzDOUV7AUXrZWdN3Pw6njE5PmQX%2Bte%2BFP33YCNq6Z2tVBAwFso3zOX9VzZnXei7iqo6zifhbCWA6NHkyhTcD%2Bakg5jLkhg4RCso554GGisa%2BQZDLE8KkOV3vQm7t58sDuII%2Bf6XPRxwnNF9PplSXNhtYjDatBhpTMUK7QBxKrFaLhAvIhxWhq9Nt77DEQhSDIlKywuUc3RW8XkHdf9oNJPPLiOL%2BM995rcAcCkLRwaQCs7INc4IBTJsNpE963nmUWBT1r53LRlYLGyE7f7MIKXvdZkwD%2FlWF6NjjmE9Hut1U5k2NaXqPPMLoBwQX5yb4BWKPeY8ZrSOs00SvHQ9xC6HAYPouXMdSDg5hOa3vXGQq9vFZ%2FDG3UXWpYmpfoJ7JGYAQ3%2BSPmVyc3QG%2F8HEf7Ii8LfGcf8t4%2Bo2nUO3DIO3RULViCecs1NuBV3KXgVSQ4ZuJ%2B0wOwGqCmrMQPlUeb5EwnOy3zIYUMINUClhwecAqzsNfyYUigqIRqOX6bc%2Fh5ms7yV1yrTyuWvLPjY1j3JpcgJeowF4MOtdyU2%2F2XCUVTm5NYNeYZ5MW58h3QXJ%2FVSiMBUdeGHKVDGdFFNoDrs5odmhoeYkhHYaJp6wRsGdBuphe2rmFOr8Gvd1IKRIVl%2BrVA%2B2l3AamKX84QGq1HTwCkUK%2FUdYRvJZ%2FDuvPjNHFll63%2BUG49mu%2FAMIe%2FoZh0i%2BpZ4WjfbyBUviEwUJc0XNS0NaRwKpiHM8RdmV3h7hidD41nV4u6YzA1Zt1PMxYXxx0%2FRHRgkVJS5wDby70KChnMBlklONCxJxi%2FmJeZtLaqolpgmYDMu%2F5Jh6PXSLAGPmF8uq1ic6EMEX9%2F1c%2BBHryRFKZCXfCQ%2BO4Ah0VtUEZBTKf6gfNwccCVtZwLF%2FGd3%2BpJrXv%2BgZtMQ9K36sDylbGYcmBi%2BaXhbxmQHyl2fJACIwPpI3tig4P%2Fo1lODyYwtceVPELcqr60B41aXe2Rm3ySoyFeOB3LPKTDP%2BH3CRXUkDD0ADhAeQRw22YbuPwXgyidQPob2L6ghruvgiGpxNQ9KtX0Q2btfyX3u4j3LUBHnh1GQ3wrstman6hP9Suz29eHiD3vSCTtkecHHJ1%2BeFUbtqKMAtUjycfKGO7qNi7gluFOaWpNCd0QrHz11JsoyIfvXWSwIA7heDEaxW233y3Ihnxwb6dIq7fDyjklDKTMyxSF%2BymY4krBfAPF9XFfWM%2BddZHMlbGNAcrhKyQq7rkWti27CqP6%2B3i0SJJdJh71siJIehCNAIuLTpNR0rlTCOy40JfmsSdjs90tBy5Bn44kz167sgqUTFgUuoJ23RT4FwnJRCZzUvLcYiOg3580UJaamnGkkMZi4405UOQzX25Bhrm%2F%2F2G3WRycM6WIU3ez%2BGOiX%2Bk6K9XadgPog8DeXd2ASzte7%2FW5miNOoU022GI0U38k9QqyGXEUvcxbkwEw%2B0JBfu0Rz6OUa3LMePo6i%2BgN21z4RBEH4hGth9CCTBnXjxdwcRHE2v3%2BRfQsOV1pZL6ZQLhnRME5G3ZXARLvIy6s9CsHtJRqBPvA9aM0l7LJooAf5VF9Lxiyth3wtnESXQQ4LFHPRPuujBrao8X72O2HKhKVVayLw4T9hZR4NIXeXDmVDJw%2Fn1zkXFb85wzbjyP5obPWy5cFTL23P6DXjnSll3orY1fnFItD3m9F1yOHGn%2FdWNj7TwnxAnFYfBUf9jbjFhzVpVtmtNHFC4R570FL3cp%2BeX1EY%2F84V%2FlvXw99e5CXKC%2FtI0MO57%2FhlQMNHLbG2aZ2A8TdDkf0ALkL1SWNQtk2gFs5B28XesCg30CoZzREyg%2B9sINw62braY0RBW89Md0jbuLl2K7prChNxeW7Qwp3zHKUeghq0LrsVR5qyJHsjc7ZacSJmOOup7UOuWiSZEzuQLQlxHW5OQCPRW00uEKOfY8PVvBWTEiAad5nHvUMcG%2FG1I4qPMcOsIFs0o%2B5kLHQtOVa0BllKhBWUQFyPj7NEIWNEBEGeOkosjMM6u9BP35oAMgwlxI7bXkwbrUBr3iNvjuIbvaDHcf2msmF11MTdnQaOyQR%2FCv2rFvtJclP10ZRFqK3v66tmTb7K0L6%2B1r6TBB%2B1sraNLv9yimDHoLKu4JnCc4uzmw9CWSuNQ1PdYJsUQPjQE7335SIqx%2BBvgbT%2FudQ3FJA9hl%2BP2hsG4xIBDsvBY4E%2FaEXDipgTeHNR2qQLaaT9wIHGHjsmSw6UaO1kcunwX3MJSRDcx6HKXWIzxX7YRmrvsI152lsTEDEdxSfhqaLbKod8hWrWDe1uErQGKZeHSSIOexnSSGQpcXxWYpKKsyAexF4g6UWllNoNJxf%2FWB2EMZO%2Bv%2BRO2kMaolZvZEDSQW7IMuRR7%2F0jQcB7T4cL%2Fvl1mbdmc3C8jUumSBLCUxjEgjStGtfYM0faHSRasxVWRMTwyyE3Q%2FXOtlspSrJVtIpkWtM9kdeCnWMPFl9cnGkwQhOEA8%2FW6rw0AE9lYn10pqwtQh6tyJD5jzWw566MOCfpIzWnZfxR8y8EeD5E6D5e%2F7vjxWhmXPC%2BMwtz%2FncW0m0Szx4ZUT05YPPxYRt5n576qWB3z9AhPzaR6lw%2FvJPo%2F7n0HzckpBKvZA1x3s025Kzm2BQZp0Byj1gdTUq7MneA97rtO3BTNq3n9v94D%2BekpWefbONFNNY5BmzfMhj92CP62JL8kmc%2FqjxXtcf38D9qidLKTlSdigWw5ZaZtEKo6afMmaFJgXyHYxBzimXOfSY6%2B1uMDXX0Osof%2BkxinTn3zmZ92d4ldydyW49QZuzLkJaAusgSaQ8FVphXcMBEdt%2BnHCMuCmaPKQPEP3fbjgW3wslVeG1tX3mAjb8%2BAk%2FnlVi903hAuYBX%2BW3RXR4qrRQgy61fcXFaHVldLCgMQ2CUt69R57stuDGEzxhikxPY6wAFlESiiu8%2BKlBXW0bqqlYGmCWeN96ycS1WoBa2g5iLh%2Bv00n0uhnYJpek2VaSsborXH24NplyNWNotTbwaJc6wxsuG2h%2FzMWO1yunkXwBCZSGR%2Fl3k%2FR4Zldr6gTtshaiCaQ%2FEkyyAb4RZhoBW7gupRCZm%2FKBPWeifX02aWxCkojJxzU0On0UZHU4IEpnSDIm0Jgf7rS2gAbAYuM%2F9ee3kvnuJZYRRISYy7PCvM9e4WxlxXrbJ4TZWlR96Glql6ZoyIu0hpeB%2FdryUqO8DSnXsdn3vDtX2CzP2ITfthHihWZ8N4o1Xz%2Btk9tUbY9wFG2mbgqW%2B1c7eQsmUMHAqiSrfuOna%2B2XUQFRe%2FuQSz64DHnLNagLNioBjAJwvXyaVmXg3LyYOBTIEW4B3e8L7r57geZTLVI1HBdoDdJ4DrOuXl4gH6Qu1b4uKgqCUbK3Fjky6rD7tIic%2FOahydmnP1Wz8mPy8g4ro%2BS5IXbAgX4FEBq6%2BgkPdSp%2FQdRNsetqoc78bNWHGz8Uj2jZVrBEY9X6nGvSNXOdtBCeoe6rVJ2PD%2FROMZLMjxjdYUc4IjdXnI8G9eDeHzmVh2Ubo012KXvnTNboHKTgDlsPqVPVTkJD2sT1gW3lyQ8TevTC%2BIht4HqFtJezDn0WW5yWBtrXPe41TQHDQPEpv6mHJqERkCgaoF3CdtIqddUZuxYKd1RQ%2FBy5X5WDAm8O9Dy%2FxPd7c5F0OXk7EhNBC7BldW4EkovrjcLauJ94u5P1kTsmobRhUby8mvVhULmtU%2BXbIVLXPvLZ2oC1Wf4aMXxb01vJQevWFJ9cXjxIm4PlDnnkrE%2BswoET3keXPyLEFvW7WPIsv5n8M%2BNrLk4ak3MqK78b3vTB0P6u9B4unxjg5NJ3DOGn9lOerTSjwVIgjh2cOx1yfdqzZQR9Ch2d1GYVWhlzXx6S3zyasZBBAEGC%2BQekkReG10wUfYbp97kTVi%2FSzh5UngqYnITFeu3FvJI8Sym6hHtAMUoH%2FUu0JU2bucVrx0wSpNbH9sUujRsknnxj9y39hPyfEXt1G9kuBqThlZIKSux3xk1ijYO45l68F%2BOVapSPT5Cr9M4lgGxOPAjHLewDfZLvstLANa2p7eMaUD2VBlAb23xn6vqqKLhLza%2BJQwgqNR8weZPNma5wh34KZNlTP70eRXTb8WZdZ0dBlg2oFGOLhyZdiKqsf4ZLPUVUQB2007el2q4sPcscWJjugcNk4n2eiPbpLSJu4wspNCad5z5aLX2qLcDF4IosmfB5PiJBrMr14QfMY4uAHnrj7K1EZJI6NJcpFbP%2FwalTJHR6uEkeMb7hmQKxCJ5C8CYr6zCoplAD2MK7Rrld%2FyPAczt8NLb74x2xwfKt35IcPF9RnO18b4BuOc%2F9WStKjVWCzoIXysmqbM68RtQYhwa8l4ZF6L3UhldIbtm4GdVo8SL%2BaTvkYA8ly7AW2eTIXuMlajBmSefCBupsU%2Fv8fHJstUhV%2FmeAmN4lP5q%2FGDcsXLFN8BD6XFASdIAnwjHzhge3hI7Y2KK1q%2FOTER1Fnyim2yVGXlif8axuvv%2F8tM8m%2F4Xlf1zmpOYDha%2BhOsH5zk3C8t2lcL9%2Bq58CjG%2FzoMCa%2F6K%2BOMYDwMbT1dcqjixB1SAnq0DjoIMjgFk6vXcb5ctOhDcZ1ScKn8OYdf8t92kH%2F9Fa%2FB0kldqsYUZY%2BNF0dc%2BqUVWOoudfuYF3fcyRwr21vjHbaGZvUdqyagLZZjYSeEJ2fLEtpLTRPtNqwySX6RIiBJsMdadncssW9o7kCvdmLH8lVPwcTvYm1loQoMnxAYvgfW8ieZd6eXFpXQv4e1HBZ5PVWbOCMV8zyNpZg90uV5sixobor9o6PHts0mgBFCDVTN4YrzGo%2B9iPH1sMmsiEeiWBLIqvKKzhKLrXDA0xPMQ8g6sRMQXSzzkXk6w2EmtjHcDddgO0KHaoclg9MYvUeFQP6QvqKPIAVhzjArAXfZihUeOFmoIMA%2FjZKTfxjALDRvjcHzyHgnpEvYf5YIrfAPFhiZ4GdH7kQwpEmMks0f4WDChTGgQBQXe3ndjAMcSZKSCcQ4jwaboTjyln77R%2FZkNP4kUttx9%2BhQ4Qpjrrq%2FzRRU%2BNGrKGRpK1iz%2BFe8truLAGnbIIjOgoE%2F5InKQiPlgnzn7coZvSDAy7UsGhMdi%2BR3e5ncnykC6NirDJ0iMODHZThuX8ozN7AbQlrOXRUIOd6xt2GV%2FLyoJUnF5MVMGtM%2BPGctku0lap4Dm%2BoUPFzV3CBtDzSg%2FDRgwBexEqtELhIS10Pm4PEmyKZESLrh8EC%2FQ8iekGXhYgMtjwyUHk9KuG%2FxazMqT3Pxkw1M%2FOIhflHaIThvxYoElysQt8hkGV4diFonYGAy9ZFc8izIGcAkkQNU7QzwLpt9hxQCwf2HG9hIrYWkle19qcrGmYeh5SdIYj2xTi%2FtBdYuYQQw0ehnHxO0kIUH1%2FOmsmvAAoFQabjDOOWdkgaTspKsIE%2FcgTXYGvqY47GvRdYdJYRyv9kAyB%2FGBJPJA26rhrLAQFe8YwJ%2FtxliVVzHgBduO9UlLirhTeF7nCMRvcaYP9vryQ1yAkPg0W9yDpSBRuHPoN46DUqLNthaRQvp22tYYQpv08r4BhiR%2F5TIS4wKXjy%2B7Nq6Ovppp35KIimjyH%2BMRxVYGBumK7Ao8oaI45pknexcXeqgcMRn7vgMO5Km2Sce8WEheaF0rDAgE8%2Fse6tJn3d2z6kVztpc0z5oglmDmeyTbK7ss4GGVbMkXoeJymIk%2BtP6pDfa9Pcygq%2F8AYQBYRLUgwgcZgjP9u%2Fy%2B9jUuXDD%2FXxRXTJLjsrPV%2Buokx1oJC6PZNQG7Fa3pmpWen2qsyCS%2BUakqatTUI510kaNAdv1y9qTauDlsCe8F54c4LjqgqRwU3z3FgqPi%2FjJ8xfZxeFHDrlqpXBV5%2BgbQskDoo8aBCaL2A5DvMbiYKrj7XCFneMyq1jHxqY28tH7ZZCHNYkVo%2BmCJdWc1up%2FQTDZuvOdRjEsuQn%2Fg26hxegwOez6LTikKPKJ1p404NJXMIenbGVYUx7wiX2bCZFZ8lldNGbD4yt%2FApVi0Y8BAKvOq3Vj9Mtbr9FPJay4K6Fab%2FQh8ZpkTMXnA0f0m5wLiBUQGIMnJ5lxbEvePKOzAc11I0sEWtZuVT6YrVYOazBirtoExagGnNmHPqnXpj8omQxGdfsHsQCoDdPyzybYS9HYmFXLs6EDRVx8GxhuLejBpQvD7qjsdfYBi%2BxYjnJDztZzrbMTxvW4yogUpkt4g%2BbtwE7L8solxBpSz7J0zS%2Bu7kymkbn27zguhuVh07ffKcTFkUPjy%2BU4GEQhyZQHVZ8mtOBatD6F9vAfuC490QVViIYZPw4BS8jxtOBlLBMWiuOx8HsjNwPSRPITQpEqEr3EkEOJOjnKrh3eShCbYfWVbxDCTJRikcSrUZ1%2FeMSEa2HNvevUxMGX0xOJsB%2BVE23Uofy9p8QO7dg5vDkJ%2F0JzaVg01xaUi%2Fl5%2BadIz3fIcZfU%2BRqHkFUyKKViOFyKFo7TC5HJU5rSetBlSJd10cLsA92Gs3TtuUOLzxhMRYbQJhT%2Fpz0B14R0M3JAa93qb2wm9fVVlIN1qyTA0abfbCEociHBZsEcZufNZS5ziiccYbKd2AQDKmJxiZnYcqNQrol%2FpNMeBFzgJopY%2FHH09f54MHdYA9iqAw8592aQn50eHe0XtEq%2Bn%2F6YcI%2F8j%2Bd%2BxRuzUTgEYD5vIop07Kxr%2Bboa9ZCmaVTZBzxqxtk1wPYI%2BgVI1bQrn1Yi3l5mI6wxUDAakr6XdQj8Me3zfvsjLbcuiJYmdiJ2ajTqJ0uJFr%2F6RdvaG3omqI6d29og1gdCED2CvAKCm3jrzt%2Bj8%2Bu3MeJqxZx%2FrHQXMgX2uKiUxqfM8OpshxJwFSmM1UAL2yLb5fCSxQ3pH3wBQXmecAGSMb%2BiXudzSn1ilsqS8czSFUgMOrmW6qJRhN1mLEZnO%2Fbpb4m8Nn43kGMaW5zCFdJpA%2BBYGgyW%2B03%2Fay32zO6S6GXhTNC%2FRMBKQadT84bOcGrvP9Xsot9Bjs%2FvtHPCPTyUoynJRM6c4r3ekhdfJbwuOg8VSmWkPD5eTD2eus3bSmvGMdzWPwtaCRjSUFYw5lonyNZKDQLYpBrvnZPolNJhiMF9jOa7vmIeELpva2imq7xYxcQUa01B6NvwlahOT%2B3niPBwD6omnypxHY3XCBTb4ETiDB0sFMCmXDnqAupq%2F9bqd4iAyiDK1FsbLL66ihIuXPMO5LLRh4DUySVpqbEmAq7yvdvEiUDPL8NP3gVdXry6od0CEiqfJm2I7rooT01LOFUBMrWXAc%2BAinVn%2BwZwgpQtnO1QqzuRPaRgLHzdzEHnsI9%2Bf%2B6JEUxF7tlwNnga8eLYaO%2Frb3pR%2BTS7EHjgWXuC099Yp3pxy82Z3G8Rr4RZxa4XzVvIUFbsTkKe5mObeaTz5PF9ULiNv6VB%2FjdvhP%2FY2SthZS%2F81QMQnVghDVQl%2BbZoayLqq5ot2xwr6az5%2FZHSl6WoG972cwrcun8RR1%2FgVA8%2F20L%2BimwboIqxj4k%2FMH0SxXPL7YXZCwQ3AlMjOuqoZQqanV6du8foFLfvjXU%2FMsDlUW%2B2QZSm7tC7iLcRLUP3rX1nYbZv9tHQEfia5efsW2CtWOspyZSAP2WsgFEuFRgD2I6l4RTOouoJLZs7U4tD8%2BTrCCC%2F7md7bejHygIijNImNta7Ksawk%2Fx2H35NxasTHBIjZFmtFpbZ5kpMkU9sSEMqapLOqRUjD1KqE9QV1%2FO4O8mLBkGIcWVavRjjE%2BZLpQSq2IEARWg0uEh%2FpDKbGnLpbefl7Fx87P3cEiuZxBQvKCgI20J2d2bOWhCYRj28JS%2BjkE8q5Bye6AGVrLuaqtqhYnwQ7ODI2%2F910xVwVIpCo%2FBLZLGFDy9opJ84yFAfzIiiVGfv4LQ2iMuKLqzVDWxSdc3S7Z9%2FXIHKOZQ%2FW0QtTw9GJylASiv%2Fd735vkKQC1bc9x1AjQFB2zU66xXQvDVXM7fT32dS02hCAHyo7Zq4Z97i%2BS5%2F8uZDCbZh07UvdKhkdK0f0g8iF%2BYHUDxqm8IbtcftID1ilTnIILY1RAzA7A2bAXTUc7VBxLyk%2FUofJAE5wiB7ZlbIBfidtDxktXAWmEToHMiZGyzHPWlzBle0RKMKSjjzdeGf%2FMtoZdeHjqQf2azzLTnAfcuMbJNG4xb0AYRzM7WQAt6jmtv0URH8%2BHYJEiCmee%2BBz0kabic%2Bva0mUCZUBMt1IJUfRHxvWK64CWKmFjGSkJpCtkpe5qGoyFKjH6xbTFPWpA0DYiaUrreu2HnuidXf3z%2FxqcNNjeMnnkMgtkHPjh7hg78Lai%2FNWlfUz2VsUyOUXczjmbtohWOKdvW%2BRz3qAH8xcnleXdEErx3AsX0ZSKpluwn5adocizgR5emPMIe%2BlwvjpwZdZE3PDXE%2B%2BvVtMnk3%2Bg%2FEcv%2FLE2C8voKLZ%2F0X0MGSsAqRPPpnnq6cza6KJFPzOFO5v771cwfiySt1OJg4yf2TctT%2BKyxCfwPSAk2wlRpbWqxmO%2BLOV5UbvRp0t1GH90TntT2pj2fwvS%2F5dVEKQOQd9OZOf7ziigcWarqjrH28%2BRBZtsaJA%2FiZFFP1mBZ%2F294uaAb1Ljm7hm6Mhqva0XHCfHaWu%2B7lWpVBVW6Pt30MyfbU9JKgnFyas4632%2Ff3e4MFnaEXlwGzCe7KuEuRcdT2uN6r3l2cT6Oe4UKE2SkUwEW9UYGzauXwALg0tib%2FLxSftEwTL%2BNYG6XADN%2FJsyADFvF5%2B2ZY5wkKEpLd3ITE0lkHzYDSU%2FV%2F1iOmqVMsjr0ur6KNVMRm3RhZys7O2sWw27xL%2FM%2BXiTdiP1mW5gKUwxudHxwJt64AxTV5ao6wCgFlYveLFApJpHNkdi7byupumfR8fJYshqiN%2B7%2BB40WcczseU3O0qmCQHTICHIn9ZtqgkNwMByAtisaAkUprUQdXOq1sni1QyHrYbL1Olgs0wkd0ZqGKPUxnSYb%2F9ad11wkaTiaSv1B3yo0xOgLw2HtTZ2FJQyJvfYiUOnVJoWVs6%2BSCusKlIBSk0%2FPpCjpdNU8e11xujbVx2CvTKa3tpeI2s2Phmq0OaXCimW7V76CY3yUGm8EkCJxXwmysOOLVytovRSSJzfap4%2FTJxjke57m8W%2B1Kul6CFF1i0OAg2D%2FzN%2B7vYA3rMjiYl7FR1VdhO3u6%2FavqcaVizFaZIXrWRaaXqTpYXjFWDbuIWSDEu2my8rMRYee3lpJ1zgEbuWZ8B7T76JL95zfZhtmmMg0ZoD2IHKRJaPQhquFcj1HSrvF55KOuWJmNz5WOjoTitOBO66bLsqcEgBef1hNR4wpHTlCYQmrOL924ysKfYDXKQL%2BpW7BxYNo9qrq2xgbyEtgRitXioBbR6jN0EssSNrSjR%2BM%2Fdx9x0X5FijMEPEMWv0QNtMcWElQ%2Fex0PB37LWOJe%2BVbrNF22wqFpchV1pCSoFMCd778hmf0WyCTSYa8BnM5fuaf9X%2BUtC%2FsvQK6eNoo%2FyIIkRTFAgbCeXhUFXkRoAL3wU3IYAOSyfVYhX81Bx%2BAmHxQdrA5IadK8BoaX56xCgisjt2xp8MBnFdh7wuzi5tSIfFcfQDaF0nEj%2F%2BwAo71D%2Br4GslSfhjsOZF1poYQcNAWVYg%2F5vKT1e7DM3cGEhtU%2B0BOMeMO7BHcrs6MUYQHnx3SHSMfByuuEuFi0BRHrpiLehpPlH1a6gYejsxtPivgWejQiPtH5V6r%2BZl399x1vyR3bbPfRDJoryynVyem6YgmLCvqeXRVmMYy3p0b9WgCGEWhYxAPfG%2FZrn6%2B4k0rkv3NCHx1Z%2B5GBC2%2FUJo29XY59iOgUQgz0iNMgaxRzkzzxcwTLpEYHVFtxAjQY6yrfa7%2F3kqmZFMVQPXXcgqwNhKi%2FGY%2BlS2IFdJT%2F11JpXG9LaTgfeHCqFXwmM28hwUbbgMRvDmLDD2nH%2BlkbNqKg075g5iQcHzw12S77YZuLQPdo0XbbW8J1uFxc4bsrCydXulXD48go8QyDMZnj9zqG7D2VN6fJ6nmC4IOt6XJfjWcfiqETwxTlmQpyPk2YbUiyXK1heaswckaD%2BZxeb1mt897MnqY2lXdfOuRvT%2BtKt8MwKYFSiNXSC1E1kxRl4jVjmHP8v2W3dT2cSiUaQQHubDDxjKhc5dMNWcTmlVMs1iAqtgNTG4uUOfwtO2Su%2B5fAJPTJP9OW6oASj5MtJlhyuU%2BXnw3gQSOOBztDPbLCQkRA5JZoNFYrbJvvVcIwMhJPkMYJnr6uBdzR1aYmGeQQQzWEdaVPCt8dddEIeZXijldlO8J2%2F6AwiKpqaP48wgfClgOO8n%2BBikd7rJEn5Dq9dCfbw%2FhYNqmsJhZSjZTbHHOXh0gnL%2FZ2%2FySftIf6SHEQKZOVvdSPujtDws48aLvQLz4Ii0bYa7y4Q0s3ut6vwgJRoCNiGvdx7EG5oj8pq5wufSn4YaQTjdmwgmF3bYWSjwh2J1yjjL1gHyH6eerLiw2b%2BWGlz%2Bnnnvc1uN%2BKjWj%2B1PSDAOLArfFQYozQj6pWLyoHceBKyBS69rBIJT3qsMQnD8nvgfBRJ7x0lfuCyHJ3Dvu8Iqa1h0M1pDIr2DL8MwvGtPvlXnrATY3h0Wt1LLNlnGLfU15c47FDivxUJ6toB1x1l2TsHuOMvMJHatQBCTv108IcUtqzliWZYy8VsqWdBXBXlcF3MZlaK5Oh7niRDERIaD8dGoEBYfqS3ARbfquJeXNETry9nLePikPcod1UJXX9%2BwzwJGl8K4aYERyhykfP2u%2B9Oh%2FGij%2BZS3kno8%2B313k4fQPCrZKkEvF4Hxt4fpER6fFR1texuTxQBdFSgNjmCcaZDqCVDGHd9uB%2FYoK%2BELo203mQdhAqjx33uK6o6WUd0THT9T%2FdFdm5DXR9DJFjPWAEX6qwfdrwmEKTwJ2YPBsbMa885HzJKMEk4vdNNDDvysxkcBaqtBmxSShH3Pa0vsV7JKJS61H4f3%2Fvb71nGB%2BInvYWJAlJunSWhEICg9ixUplUWUTVPNZMQMlpTharhCaY6V%2BBDdITJB30Hv0R2rdPhm6fP9LMOv1%2BL1FM8IaiYharEXYRXJ38h7FBd8be2Xp3vwTOl5YXuImBZzGfpcqwwugE5h3b9vcpIIRthNoxyLcC2Rpk9XaFrCDP7usTFwtvR5UVLSra%2BjGCko2YxVeiWJOCMWDWhbv2TGa2QGXPU3HkQPnZPUuc%2FmJO%2BcVukcX2Qn8G3VTevAKlcFh1zXakaQhCtDkXKY%2FXFSCw6eS3eOMMIGRzlb5cVSm3eAx1J9lmPEZjRrqBgrJQBDuDihYQWf861Wwn3Cnpxe07md1Xih7%2Bg%2FJkK3UHwnIlignm4gJ1r7GPHIpT7PLHcJodXUh6INKA4e3LXkXyqx4hAl8CKAuy%2B1zPH7N3Wj8LSTDbzucUz%2FZXm%2FoyA0%2FAXJA76rBc2FjjIZLyPc%2F04q%2FUl5RZOegwtB9oi1CMKEuAFzJoEHy8tqIgGs9UhhSXhk13W1o7HtzAq6oGT2Vp%2FMZf%2BTZ61iK9TL1kRSCp7p%2BQ9tSz7XTIwqnJuEEWD%2FT2VuYmC7WwQyu0zmyrzqick21lhoc06f%2B90G1gxQXdpwHeHp6yGrwN20rrOvOShR9jpVyhMhJLI8ld64zy78t626zUyDUWVypQgXj%2F9owrB4AzKDlV351kJQdttm17RHOmOTzOeATkztXM0qh6Lxv034gaqiFsjLlnGHVv5nVymhy6XQTyPxjNeRi4NqZ0x%2F75quWqkWI9w%2Fp3K6ZGaJJcL05isVwv737w1jpKKjp0IXqBvTerJJARnLOoNHJbVkoT394u7HBkX1UXxmTcwC%2FeOoyz0V0yxhlbbMrYF7UJ%2FS0cLX1KL6p36DkokfUR1WyT3tx0tDwcfb64U9bY8gkib0wLV4gSCL1hab2YXvdxs5X9TewEk37%2FdPOUmuYEqe7TtJ3KEooF18xYiUCikIyY9lwwXU128RPsR96LYe%2F26r%2FalATNRW03cih3UUzvtrHC%2FSXrFI6pPgkhF6ySYbULnLK9FfYYQXqz37tUb4tVebf%2Bpz2gPiwjCj4v2ZSakygp1h3y6zn4haKvEZP4El2poqtILNju1cUxyiIzImX5WM58ih7ESOJN1qDTYMG4K92b1RryIBhBFEAzGtP%2BMkX%2BiHkFYBoR3yjEigCAFGUnBl1y%2BVEC6zYzs7kvcTYeHfnWtyblQ7hxY9dxiSHBlJqulKVj04RUV%2FlhimBy99adUWQpzLs3qvQHFRgTQ5vi1dbJrfN2dK61qAxN4JVySs5V%2FxKN%2BTBbI3mK15DayxzvrKXHa6YV37V%2FJ15k7V%2Bqe3fJilrxzV%2BrawAWVpw2XnC7IpPNNJn4jNoeyYNyiKqdIhJ5ahsvAULIabL%2BR892Cn5vePEmNVBRKAOzkHC2uaa6LOH053i9AiVev4iD%2FBa%2FDgz%2Foi04h4QNnNWqz%2F42%2BY1jVdjoOvikZ89iJHG%2Bf0L0ut4IPY32tCN%2Bnje0Nwj9GSHFtzNhkp7XN%2BkYt4GYfDFnI6lrB%2Bw5xPeMRdnI%2FPwf4SWwlvA8MVYi255flzeO8V4Gxtp6DkG4vcRMJqibTuzRooLn%2FOfcj%2B6jC0YkFC4TG%2FW4MKGR3Bxj9csp2tUeikWtZg6nZ%2B%2FBcw%2BEedfe8hcRvrIebb1NqxFUp8AcW6J43ESZdMkTgWnwzPkzkBA9FPHPHqy2l0O7jnen6tm695lB9SiPRPsH0vLTKsDU2%2BtOB8HlUlypO6oWcptdExyAVv58fG9JueKo1xhVwRdkAdkqNvLH4YZ0h8zuk%2F77CPEvH5PfVne1U6CUONE%2Bt1NFbyJSVK2HPDjHMM1RuNLgyan9MzFSEwCRptoAvk%2BnrdZ03fj93Ikul8dGebzxvzXLIFcaZyJy0SnaLm%2FHrCvhVPTyFLZtR%2FqFxMdoc%2F9XWcYHk5ymXNxVM0EJZx0hTn6jEzAhZON5Hnog21X%2BFIdS%2BzmwsBqWBOJ22nTbhApCCsmIN%2FOR%2F%2F0yTHAxdOTxt178zmQonLxlBtxBhA06gywQm5UX5bFCsbS8h0Fc9BZAMjdolzwC3DSmmTXT7HfPJfXLtoBHVGKZKuDCChyjqqNuux9se2MXNXGfwLzgtmMogKCsR9jVhZK2g7COhcMz7tSbtSCTC6njK65MclNmaRNBpID6H%2FzGdOnjaFFkuzVUF78FlaGWkK7HZoM32UFITGY4wv9b3n%2F4HUzqND2zD43IwU5O0fWoPpOaySvIDeLGI4MWo8lUfDEzcBU4VZWj%2Bxw2UZqnSXXeFaqZU4tHJr8gtY1VsOaUPnN5dujJRbvEDmL3y6Plxu4qsJMyosxbEVrOeW%2Bd7kEnV4jGime4%2BjrJc5SYq5uWadZhVOjeOgi8t46fBGoQ%2F2ISWT6D1w7U%2BFDY6vFX3%2FBaKtcpxwJoyKFfIlHdQJj4VZXjP4WVQx7N1at6UldFKn%2BrnDOyrbrJ7MRfVZFykfN595lKl8n%2BE2kjau%2FgGirEroQKFBjC9c1zpXYD94tdHc57md5lpMVL63lC%2BL5Pi8NTG9fSLpnzAh3F5Omocnd5FlnPHOc6k6yIXa06VmnR8wdfwEg%2BePvCxBhm1IM0Uhp4f3HDAa9mzFDkKKfXNHgLsMwFuWG0%2Bvn%2BSEFdVm2HIt5B2vc9%2BwOSnmLL3ck1LAuqxD2OPHoZAkrWVgZpBmxbK1V4PAZ4m%2FBKdAv1LT573fVtNxN6QKDWYr8%2FOHbw0anRGVZ%2F%2BvYAKUD9pfVNTQYe7EjMB1hFsS3YSCd7DtOCk8FVNDmzo8ZIECgtxO9BU3xIZh740Ab3q3b9ViPOS2SqT5NFANs1LXlklPJcp7mFuQ7U1ck6QGDzwMbnWk1bVHoBVoDLsd4HvenV82vk6XBBaLLflmmZc1uWAVWDe%2FgwFzVtTyYnpJ4yGbVVag7IcQGUCUjJoqMcd9nYtywOO8ymWe1m0ZwnWxDO%2FdljpmrQoS01hFw6Avk23Mb%2Fpry4rTR32GbEyZiYVPq8ac12VFkhAYLxw4vdf5ktoRZk3uG8TSHhalRedgnQ%2B%2FLKK37I56x%2B5EmQ7TlTIF3489TgD24lGiRoHFDCR%2BXWGVt15Yb32zT3pWsH6CuN0aUXZbN3mVtZAidiIBYGsbC3ixJHWUHrXWJHlsCtyDGG0rNH%2B%2BX0uhQU%2FH7LjyFoK8tSTBPyb01Gwzaxahqlo1tfmS1u1FdY0dGTT8EXyU0XzT9WlfRFtUNDfhEJNCfIEusk7gWtpEG%2FHAqFx3emMY2T7pcclFSl98mt58PLLLofuaVtnywSDxCCjvLB2lw62KlUZPEIQnfVEHnuBrqVrIk8guVfzHPH3SCGEjYMEvQG1WJ0ArGdNZEFwGLtgtmh7GkOdZfADzg%2FbxXHcpZZWOSCuDGJaZPC0uK2evruZTwCs51IIHiKN7Lh4KtJK5XeTNq69UOGBVC%2FNrVAkoEiuBYYavNzNc6hnVafXhTlhDLRqpqVxBTRHn2QDw4zwvju1MfOgxKBDOyH%2BU5gBur5wjoCLA32mh5pwLu9e6bdOBFXtZi6wJ%2FhrkBl2LrykL2mH%2B%2FBsiTocj9c7NvXfmCnGVkoLnCGfRXEIRE6ZLrq4l%2BCyUV%2BmiAVk07I7gwrcY9eq0NNMbt%2B9%2Bg9mqsE33YYIDV29dMEhZWnBIe9LfYh3qarT61xCGc%2BVEgEoYcfU5DmigEAvXEW3lLv7Bf%2BE64eO6OAQx%2BkACVgM4qUixFZrB2DRz%2BSZyY8aLeoJQoo1elpN1tKj2TE%2FCvt16bkABU4ZABuK6SB6kTqXcE8W%2B711xESZlcgt1W0WSy5E1FS%2BCVi9HBeJ7ntpBHeTEnpzIzaxgTFoepyuGb9%2BpzJOIQ4u%2FC7YM5AFuns2UJR7lSowOdGrla7nNy04Tz0%2FCAxcAXsYWoCL3uwY6iHWY1bODynGR%2BKHE9gAC6NmlU3isDy4wmWsTzGHpDnjvkljKGKQ%2FPI2zigiQLGsN3iBfp4s6TozcFyAyYF7iK5BX3mHVIvGZ8el1FPFblyLiS8BBNyhe1BXzSDX1MerO4AA2by1Jj8bQ%2BS4wiKv%2Fh0XUTuZBtLXrFa6Qvjq0G9Jq%2BFDv26jlT22%2BGLxeWDoviZkPzs9mabFBGAzfuGJ4%2BWUngvh4k4qg1kdAf6bdmGyzUmaorjPGTsidqqttcpIZbOgfkjt0wa0u6mKd%2Fdouw%2F8ZIoVAoJppu4tz0ZggDhJvuR%2BHCXhy5itEVAuke0C0l%2Fg7NU%2Bv1sgzLMrZG5fd96BWQ%2FUJZFn4STdVwZPk7LMtO%2F%2FJtjdRHlxvwAQYZb9OyDnaZO%2BlhDD3rivZqBuMD5Y9wfhcOJfPy6MgQxx6D2dYN9PKPvMiWelWybkDN25VQwnT0DONWkQQkcaNzUZHcAHWtXiLWrsCr5%2BrBjKyByQu9t4L7rJrS%2FhJPlUcC1BusCV0BXKNbSp2gxcpMsHWwIo76AH3rNbmI0bSMBgoimSYXBFHLp%2BxGkpU8sjl0CSKIYJhIGrnG4nIze7iuD%2BEb97eJD6SzpPduwJBCtczvLl6J5fhLPMmPkIUxtV1wARkE5I6YwnLWOStNs3DGKWg2fSryc0koeL4Q4GVwBMGKo8AnuFK39670z5fiL8lKfRbnKE%2BCAJhHjmaAUr1nFdDVRz%2ByzGYJ2gnlIrA%2B4ows25WOsWA0QSfLrWI6wB3uylEIMiUgSlhk5SvIiSty%2FgU%2BWQy3dciyRGvy9hb8x0Epu2dpdSkrRq8WxyJqDsjlgfikvJs5nnojMkBGDXMljsm7vuWYSPJUdqJ7NBT6KWG%2FEewu%2FoK2Ab7XmVb9V1MrM75KCVmY%2FU5pkNTc5TLIFyrusnFpT2dn8d3YtebLFAdAuS4eUaQbd9TqbgrKvoVbaygDX9ZNYPlsCXNa%2BEwVsNMQmp6hRrcItBcaf%2FPCGgP78kWBbyZXKo4KNgBJe3h84yelv7he91lZ6fnfMvZZXoDUl0%2BUO%2BVfncBq1bAG8EAE6cgPjiPJan3TclYX8hwbCkaNIKvnwBCwYHeZ9praVnrCKeNDVWrTDIklP72Ti2w93v4B7V%2B%2FFj0NzOAh2asLIUVM0xVuKXbXkpZriBq0YcIHqDAwKUr5IMxfTGsGAh%2B21nVPQ27QHeZnUFWQiqQvMCcxk3k%2BWTDu9VgmsV0iOSYbziZxXkNS3QcmG%2FFbTw%2F5Whg9mtyKDGX4pJYPrzrZ8qkwOqcjcTJh2cuYk9TVGX4NOH5dkc0jE%2F0%2FFM4GTP5ZGgjPAF8jjj4laO89pfsLXiX5Bi4ObF1Bzfj97xTlELfg%2B9iR1WoJ07BVqVAA4X%2FJPs7Y3kYpb4ndYwN45M4ZGrAVQ0makpts0kQ%2BIQvaYV1mRnVF45WjhoJBRfxpy7gWXldy5bR9SUJ0wdlXMyTxX3zAhgI6OqveByJXtoLvgkzrEolHcUfCWeUQV%2FJkFqQKN1aT%2BIvP%2FFqwkUXPnSd8xEKxBvKpsXbACyoYMa4z5eSBtKPxjrmpEx7MU9MQSeFlD1Gwqh2wQY%2BW2qZyi9F6kZFKadHS6p7LeGk7Yo7053iCO%2Fvm42APBnwBhpqCNKh2l7NRTTscjlAk0eq0AqL4JbsGQc8wDrMwczUFHZ%2FFW9IxLWbnPZ%2BWZNbHOB%2B%2B6mAIjNP%2BvYJ%2Fn916MQNTklt6Ma5yHdQwZawENMMO931z7xwfXkq%2FeL6F4%2BJndcbJVIzmNFMm4FD6425ICefKXEvehFQdrFiwTpN9zKHx520OD3LJra5M5DJ6UYFfdWoEawMs1yJ2KN6d4Q8zcfZuZb7x03m%2F8s%2Bf1WAUmlJgtWUwLS7GJ7ZVNEpQXLKbymMFVOXIVV9DtFOo6BjuOgLbCy93fxWtcA5KJGsWm2pv0NvRm2F2G2a50eK1BaFt2u6qRTfP7iDrhodtjwTCZE2UFc4LN%2Fo8gjnFcfD%2FRK0Wk01ScxZQ1nUKTey%2BJlZO0qxtGJShs5sOVg8WyR42WVZgkCKVEys52yYJXZWewzoVOcCvvXtWdUonPa5mZ470iUOH9qAhk9JZbH9HN1tfb16dVZCT40YK7u6tlTJGxaJ3Q%2F3eTRup%2BjDRbh5WTkktdUcGwpHvnjIJovb34CQoz5CR9iAn4ebf77D5452Guwz%2B7A7Xnh0hiMI%2BZNHH7k61V6GIBW6dBssmasrRFTcpsn50WzliVkhlmsUFd0ulWKJNf9Rw9aN0UfhwsG28fjBDNsvp2hOXDLKU4frTNMNSVxLlPfnfe0veslIbZG93jGStQBwUMkCw%3D%3D&__VIEWSTATEGENERATOR=59A5EC9F&__SCROLLPOSITIONX=0&__SCROLLPOSITIONY=0&__EVENTVALIDATION=FOy5WCnELE6WRoUAkjOH6YTpsw1UpF0sfDdMmwFrrCepSZA0j6uWp2EGyMNeVbbE8YdiJ3np6780ZWoOcR1reD%2FRYRry9CRkCgjsYkMqNUYiT%2FAnAcb0LY4U3jx1bpKWeLYhKIDUffJ8lgWkxNy0OBIFdUhBKvG1O3C9PLUsB7B7fDmpCmOA1Gwdc4xHneZqTMHUKvCVwokjmvbRTOMVOWgss%2Bj%2B5lObDtFum2VfUEE7T23oLSH%2BspRhRm2pDp3cI2GevFPDNkdt2XvOqRkxEAOz%2B9EDvMIGzkShRz1pu%2FxYzEtC4%2FREETinA9Mh2wh6%2F1O2VaRi3DivA7RaNbW5jfF%2ByLDQXn9c30CqapvT2TjJT0AdO3A63SQyndn6gMwELEzC9SFaBNQjRLYVvkfTKRaXGtT974rUrDrKfdntF2JIktWdWWR4sUJNWcMyiIRK9Zuu18iffJt1CkFGL3K%2BQygBms7U%2FxnGJpmMozqDfPZq6%2FXJSEn2z%2B1v7pGR4GKaeNxmiZW%2Bk2%2BEmJSbNvdcHOiIeW6ExZM%2Bskgr%2B9GiSJt6bnsOM6AvHuXMPqoHo6aK2Frf3SyEwSGbjhmJ5ZaOvyTXZaQQfuEaMFJdqQ6M7%2FgmfBXeYdb8tWilMn%2F2wmgTEhoKN6is1yPzBBThuh%2BFH0Bx0MHCIHhtXYC7uTkAI9WlKpjGdcofKx90eaVivN4rCPMQ%2BUEhkzePVkljZdJ%2F9jN0r%2BalbLs9oqBuY79RflKVLhhNt9W%2FzKGqeNsSOQm5W9ic%2BRBIZSfj3TX4dqaCFp%2BfM8vLwcZcFFZyL9QqOHsXFQEjHxgnnCU5AA3p2LVbe7kJqvJTgW1OhujPSwm%2BHqlq6go%2FI7WLEsOeqYmIOriiyB0Tx4%2Fmp1RBuYYVkfZ1Jo2zseCr6VXrrdP5rLEmcJ%2FxGpbJjqhIJU3fKCWnSR50HRhRZNscifDEWsPm1mR3cN9lEfESOfqauhj0ZVYGHKjR%2Fup3GDG1iWFC%2BmypAqkId9M5srzyzRiLp9AB3aBFbUlDeiKyy74DvJeX7PpBoyZBeTPdr0vwg8BfheRocKiwTnA74vuJLEPP3HVRLRTjuhIDAjDRBChP%2FdESQTLdLyoGp6a9dut78%2FdyAEOcHBDvDXCYoh9dcf1owgdSPchM4lnZy1k7lOBp%2BUEnnkEBR8uI3789%2FJOgGDm6JW%2BTQJXUwNj%2BL7AO4miMu4n81fYaEPZMhDaZEBMbQD%2FSi2Qm%2BXsVJSZA2kFTw1n2PcibNRqE2SAdUEE299hWvMrc%2BvdYNTNQbvv1PXm9jHmgRBNOq33SP7u6g1bxG06afwdbemYBueMigv5roElrgTictyAjD4GNiJ8fDb%2BCAaZ%2FhwZ1e41scTAOesNJtj4SzECBykB%2Bo%2BDs7QRnySqjdlYGRmMVjjF%2BAKm2acgDR2jg8NWHm12f9M29VfUAOCebZ87%2B%2Ffafl9qwbRgGU7mZyLsyUW9RAgQj9OH%2BAnSxqxfJKJ%2F7qsCQazoOIzuy5VCFcr3i%2F%2BQdFiy0aNuigZZ97pU67PEuvM7LGVde4F9%2FHLWpQtg%2FOnkrwex8EWwnp9j5UWKqyyXsyF1GOF8Bdxw3TsJGiMxqh4NlsaUIntU3SjQ%2FnMUAIxxsCPf36rjMuZC2eIejQuEUoEq0I4XvfLlkZpZ3FE%2FwHN3%2B9bXBgKHvSFKbemNzpKXesyeRGl%2FPEjq4Insh6U7LZ8UunNX9S9jAM6IZmemZ%2FkIr%2BhRvrnFggU9fojXGQ4WZZXorD5OwZnpsd6nCJ6zmuwKHbqdD24LY5b5Xg93Q%2BGDCu5LgjZA1XjenRIUd3QXFNk%2Bh2cb1WRXvJy97Yj93nmnSowzdS0usj99hEnyUlHFsjTNLgvCFpydM55SuGQmnKBXHhozHOU97tnxT%2FJULr1NRTBvbU6VEUSgFSgQQyqP2EuEChb4%2BC3xVSjrMzKkpRIXOewHE1wTl2H8BByUH2RhAi7BHR%2FhC9fzrTh%2B9S%2Fa7A%2FKul5dXHg8OrJk6B%2BJIrdbQ6fu0UmyAoPuz2TxfUIjYDlueMPiTkJVHdCQEtqnRv36%2BR5YOU6DUxsJkic3MPKEejKwKHFi34R6aaHb1JaGVkWX7BvD3Ra2w4lLv0K9MBY1fWfKrf%2FCsTSWtxAFZ6M0780l%2F%2FhesA7TOtNq9DUHgM4vcryEnYKjQtUXw9LsXexGYl4dtGYLEaOa1fliumLDcg3b9AgnrsczCnk2W9PpVZuSL%2FNPMKN%2B8UcX3SABZy4kgXrUR0W4aWgStVyZzzw%2FKVW8AVj9pdcqgxlaJaoPXpa%2F1WFLGAr71uL3GuTXa9ITC30%2F8i5zFk5nI83xKreHdHsPBpR4PCT0b2i0p%2BXHWFYu9POnHA0uFGe1Tfr5DyYktqkiJhBQeNtoOQO%2F9vkKpXlDBmZ1cLHFMzw62AUnyQILTIb0iirZlJP4HJQd2PBlPhKdZzPAbN8oNmEBgUJXSIJCp0viAc0numowLi0SOqogjJv5dJovmmtWdGIzOOS3eAEyHIUeskQFxguA3BlhfuxSfh0YDTTe930PT0ogzwy7DKQvLfSxWV7CwpZxfDgJa4hmWPhM1KErQeXQTOIrrgczjobotJcCbq5tOvwa%2BcMHHTOkTh5nCN7PrLLPQcoHaHVzlBP2IRVb%2B3%2BzsykvJKVOeuCEd9AT%2BPQTPvOH%2BPn7q%2F%2FwX8DFs7eAanMjgwNgRjKW0j9RIk%2F%2FmP6ZTawRWbx8q1YYnWXbXS7rOwnnGr%2F48j19DmdY8R%2BnVYIvDfirMRHg0vzLnsp2vY9zFbPB0LuTwHKXtFObJUxd8XY%2BlqA6sbxvFwGCixlXUr3MmwMh%2FEXnATbMVFGiurhfylNORbH%2FRgLrf%2FD0H7XoumeB7HvSSqFGwGD%2BCSwo5FcI%2B5GeOZU2QsmYkTx1n8b%2BJNEDPTE1Bi3Rjq8WPhIJnzod%2BaIQ%2BAbY7zEwt8AI%2BAe6DYPF2uOlMppgmblccRtki18ZgHQEnkNA5VYGPTZhT4NXiI41AZlCOKxCiCcH1qGabeaQwdYrhsv%2BQQhlBbsZH9o9P0zkdzqOo3j6Cb%2F10LfR58hclYOE2JkFcydG%2BHR4H%2B7gUBML8foHsU4SU9cdL6EqJNBOgc5jZ7Y%2FqW%2F1y4GZvZMf5K98%2B3XaB2wIAt%2FksjgGTfJz4rwM6c1AoWmApJUWlBWIGOCLAVSSf7dUtQs6cTDM7MbFqqlU2wtuwHd%2BMdQ35zRX%2Boliscu6wY%2FFv4oXZ1oROKLicQI1TTJz1nu8%2FHTq2eOgbLtj7wxY4WUZmtXPHXrrjuQRwQbTBsd8IRPmiDmlhSP6%2F7pa06UQOVyPLvN6ND6sTgojOb0Nn0NKoxFLMhyuU14jSijwhZJ5FJnrmxzLQLmbtk%2BMwNS76Pbe%2BGclG4tMFgmiR2NAYYP%2FA%2F4rxvRJ8ESLP%2Bg1VWU40kNrFbJyJYPmV%2B15J0JjmhUZTbDYWsb67PbzdzA11xP7So1qkpWDieH0ZcAH%2F%2Bnq5Jg8ltqWMMD3jf%2FvPKC9s%2F6NHqyMx%2B3aqPp2%2FctWpNMkWWg%3D%3D&__VIEWSTATEENCRYPTED=&__ASYNCPOST=true&'
    updated_data = data.replace(f'ctl00%24ContentPlaceHolder1%24ddlTehsil=1',
                                f'ctl00%24ContentPlaceHolder1%24ddlTehsil={tehsil_id}')
    updated_data = updated_data.replace(f'ctl00%24ContentPlaceHolder1%24ddlDistrict=1',
                                        f'ctl00%24ContentPlaceHolder1%24ddlDistrict={district_id}')
    updated_data = updated_data.replace(f'ctl00%24ContentPlaceHolder1%24ddlSRO=1',
                                        f'ctl00%24ContentPlaceHolder1%24ddlSRO={sro_id}')
    updated_data = updated_data.replace(f'ctl00%24ContentPlaceHolder1%24ddldocument=17',
                                        f'ctl00%24ContentPlaceHolder1%24ddldocument={document_id}')
    updated_data = updated_data.replace(f'ctl00%24ContentPlaceHolder1%24txtclaiment=10',
                                        f'ctl00%24ContentPlaceHolder1%24txtclaiment={document_num}')
    try:
        response = requests.post('https://epanjiyan.rajasthan.gov.in/e-search-page.aspx', headers=headers,
                                 data=updated_data)
        with open("e_search_page_rural_new10.html", "w", encoding="utf-8") as file:
                 file.write(response.text)
    except Exception as e:
        print(e)

    if response.status_code == 200:

        print(response.status_code,'<---------- Response status')

        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', {'id': 'ContentPlaceHolder1_gridsummary'})

        rows = table.find_all('tr')[1:]

        headers = [th.get_text(strip=True) for th in table.find_all('tr')[0].find_all('th')]

        document_details = []

        for row in rows:
            columns = row.find_all('td')

            doc = {}

            for i, header in enumerate(headers):
                if i < len(columns):  # In case there are more headers than columns
                    doc[header] = columns[i].text.strip()

            registration_no = doc.get('Registration No', '')

            document_no = doc.get('Document No', '')

            presentation_date = doc.get('Presentation Date', '')

            try:
                if 'Presenter' in headers:
                    check_presenter = doc.get('Presenter').split('#')
                    presenter_details = [
                        {"presenter_name": check_presenter[0].strip(),
                         "presenter_address": check_presenter[1].strip() if len(check_presenter) > 1 else ""}
                    ]
                    doc.pop('Presenter')
                else:
                    presenter_details = []
            except:
                presenter_details = []

            try:
                if 'Executant Name' in headers:
                    check_executant = doc.get('Executant Name').split('#Address')
                    executant_details = [
                        {"executant_name": check_executant[0].strip(),
                         "executant_address": check_executant[1].strip() if len(check_executant) > 1 else ""}
                    ]
                    doc.pop('Executant Name')
                else:
                    executant_details = []
            except:
                executant_details = []

            try:
                if 'Claiment Name' in headers:
                    claimemt_name = doc.get('Claiment Name').split('#Address')
                    claiment_details = [
                        {"claiment_name": claimemt_name[0].strip(),
                         "claiment_address": claimemt_name[1].strip() if len(claimemt_name) > 1 else ""}
                    ]
                    doc.pop('Claiment Name')
                else:
                    claiment_details = []
            except:
                claiment_details = []

            applicable_value = doc.get('Applicable Value', '')

            location_details = doc.get('Plot/Khasra No/Landmark', '').split('#')
            location_details_dict = {
                "khasra_number": location_details[0].strip(),
                "plot_number": location_details[1].strip() if len(location_details) > 1 else "",
                "landmark": location_details[2].strip() if len(location_details) > 2 else ""
            }

            property_address = doc.get('Property Address', '')
            address_parts = property_address.split(',')
            address_details = {
                "village": address_parts[0].strip() if len(address_parts) > 0 else "",
                "tehsil": address_parts[1].strip() if len(address_parts) > 1 else "",
                "district": address_parts[2].strip() if len(address_parts) > 2 else ""
            }

            doc_final = {
                "registration_no": registration_no,
                "document_no": document_no,
                "presentation_date": presentation_date,
                "presenter_details": presenter_details,
                "executant_details": executant_details,
                "claiment_details": claiment_details,
                "applicable_value": applicable_value,
                "location_details": location_details_dict,
                "address_details": address_details,
                "property_address": property_address
            }

            document_details.append(doc_final)

        for doc in document_details:
            item = {
                'location_type': 'Rural',
                'district_name': district_name,
                'district_code': district_id,
                'tehsil_name': tehsil_name,
                'tehsil_code': tehsil_id,
                'sro_name': sro_name,
                'sro_code': sro_id,
                'colony_name': '',
                'colony_code': '',
                'document_type': document_name,
                'document_number': document_id,
                "document_details": [doc]
            }
            print(item)
            print('Data Inserted!!!!')
            output_table.insert_one(item)

if __name__ == '__main__':
    print('Crawling Start')
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        print('Sample Input Count',input_table.count_documents({}))
        executor.map(fetch_data, input_table.find({"District_name": 'AJMER',
                                                   "tehsil_name": 'AJMER',
                                                   "sro_name": 'AJMER-I',
                                                   }))#----------Change name here------
    time.sleep(5) 