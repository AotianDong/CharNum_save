from selenium import webdriver
from PIL import Image
import time
from dama import use_ydm  # 第三方打码平台
from selenium.webdriver.support.wait import WebDriverWait

# 对北京市交管网车辆违章信息进行爬取



def time_format():
    """对时间进行格式化

    :return: 返回当前时间
    """
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 格式化字符串
    return current_time


def element_screenshot(element):
    """区域截图（对指定的区域/元素截图）

    :param element: 要截图的元素
    """
    # 截取全屏图片
    driver.save_screenshot(captcha_image_path + "full.png")
    # 获取element的顶点坐标
    x_Piont = 850  # element.location['x']
    y_Piont = 717  # element.location['y']
    # 获取element的宽、高
    element_width = x_Piont + 150
    element_height = y_Piont + 70

    picture = Image.open(captcha_image_path + "full.png")
    picture = picture.crop((x_Piont, y_Piont, element_width, element_height))
    print(x_Piont, y_Piont, element_width, element_height)

    '''
    去掉截图下端的空白区域
    '''
    driver.execute_script(
        """
        $('#main').siblings().remove();
        $('#aside__wrapper').siblings().remove();
        $('.ui.sticky').siblings().remove();
        $('.follow-me').siblings().remove();
        $('img.ui.image').siblings().remove();
        """
    )
    current_time = time_format()  # 获取当前时间戳
    picture.save(captcha_image_path + current_time + ".png")  # 以当前时间戳命名
    captcha_path = captcha_image_path + current_time + ".png"  # 获取验证码保存路径及名称
    return captcha_path


# 定义号牌种类字典
car_type_dict = {
    "01": "大型汽车",
    "02": "小型汽车",
    "03": "使馆汽车",
    "04": "领馆汽车",
    "05": "境外汽车",
    "06": "外籍汽车",
    "07": "普通摩托车",
    "08": "轻便摩托车"
}


def user_input():
    # 遍历字典，输出至控制台
    for key in car_type_dict:
        print(key + ":" + car_type_dict[key], end=" ")

    # 在命令行与用户交互
    print()
    car_type = input("请输入号牌种类(01-08)：")
    car_num = input("请输入车牌号码(字母大写)：")
    car_motor_num = input("请输入发动机号后六位(字母大写)：")

    user_info = [car_type, car_num, car_motor_num]
    return user_info


def commit_form():
    user_info = user_input()
    # 定位到号牌种类的select
    selector = driver.find_element_by_css_selector('#vhpzl')
    # 选择option
    selector.find_element_by_xpath(
        '/html/body/div[2]/div/div/div/div/div[1]/form/div[1]/div/select/option[@value=' + user_info[0] + ']').click()
    # 在浏览器输入车牌号
    driver.find_element_by_id("hphm1-b").send_keys(user_info[1])
    # 在浏览器输入发动机号后六位
    driver.find_element_by_id("wffdjh").send_keys(user_info[2])
    time.sleep(2)  # 暂停两秒，点击输入验证码输入框，获取验证码图片。
    # 点击验证码输入框，获取验证码
    driver.find_element("name", "captcha").click()
    time.sleep(2)
    # 定位元素的位置
    element = WebDriverWait(driver, 3).until(lambda driver: driver.find_element_by_xpath(
        '//*[@id="queryWF"]/div[4]/div/span'))

    print(">>>正在识别验证码,请稍等...")
    # 调用区域截图函数和识别验证码函数
    captcha_code = captcha_test(element_screenshot(element))
    time.sleep(5)  # 暂停5秒，识别验证码
    # "hhhh"表示未识别到验证码，用while循环确保能拿到验证码
    while captcha_code == "hhhh":
        driver.find_element_by_xpath(
            '/html/body/div[2]/div/div/div/div/div[1]/form/div[4]/div/span/a').click()  # 刷新验证码链接
        time.sleep(3)
        captcha_code = captcha_test(element_screenshot(element))
    # 将验证码输入到input内
    driver.find_element_by_xpath('//*[@id="queryWF"]/div[4]/div/input').send_keys(str(captcha_code))
    # 提交表单数据
    driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div/div[1]/form/div[5]/button').click()
    time.sleep(2)


def captcha_test(filename):
    # 打码验证

    print(filename)  # 输出当前识别验证码的路径

    captcha_code = use_ydm(filename)
    print("识别到的验证码为:", end='')
    print(captcha_code)
    return captcha_code


# 验证码图片的文件夹
captcha_image_path = "/Users/dongaotian/Code/CharNum_save/captcha_img/"

# 获取cookie
# cookies = {i["name"]: i["value"] for i in driver.get_cookies()}
# print(cookies)

driver = webdriver.Chrome()  # 实例化driver

url = "http://bj.122.gov.cn/views/inquiry.html"
driver.get(url)  # 浏览器拿到url
driver.maximize_window()  # 最大化窗口，便于定位元素位置


def main():
    commit_form()  # 调用表单函数
    # 获取结果
    try:
        # 若查询出结果，则获取结果，输出至控制台
        result = driver.find_element_by_class_name("bluedi").text
        print(result)
    except:
        # 若未能获取到结果，则将错误信息输出至控制台
        time.sleep(3)
        result = driver.switch_to.alert.text  # 获取alert信息
        print(result)
        driver.switch_to.alert.accept()  # 执行在alert上点击确认的动作
    driver.quit()  # 退出浏览器


if __name__ == '__main__':
    main()  # 程序入口
