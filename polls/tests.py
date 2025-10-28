from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from selenium.webdriver.support.ui import Select

class MySeleniumTests(StaticLiveServerTestCase):
    # no crearem una BD de test en aquesta ocasió (comentem la línia)
    #fixtures = ['testdb.json',]
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()
        
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_staff_user(self):
        # Super Admin loguin
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        self.assertEqual( self.selenium.title , "Log in | Django site admin" )
        username_input = self.selenium.find_element(By.NAME,"username")
        username_input.send_keys('isard')
        password_input = self.selenium.find_element(By.NAME,"password")
        password_input.send_keys('pirineus')
        self.selenium.find_element(By.XPATH,'//input[@value="Log in"]').click()

        self.assertEqual( self.selenium.title , "Site administration | Django site admin" )
       
        # Add test user with user create and view permissions
        self.selenium.find_element(By.XPATH, "//a[@href='/admin/auth/user/add/']").click()
        self.assertEqual(self.selenium.title, "Add user | Django site admin")
        
        # Add name and password
        new_user = self.selenium.find_element(By.NAME, "username")
        new_user.send_keys('testuser')
        pwd1 = self.selenium.find_element(By.NAME, "password1")
        pwd1.send_keys('pirineus')
        pwd2 = self.selenium.find_element(By.NAME, "password2")
        pwd2.send_keys('pirineus')
        self.selenium.find_element(By.NAME, "_continue").click()

        self.assertEqual(self.selenium.title, "testuser | Change user | Django site admin")

        # Add staff and permissions
        self.selenium.find_element(By.NAME, "is_staff").click()
        permissions_select = Select(self.selenium.find_element(By.ID, "id_user_permissions_from"))
        permissions_select.select_by_visible_text("Authentication and Authorization | user | Can add user")
        self.selenium.find_element(By.ID, "id_user_permissions_add").click()
        permissions_select.select_by_visible_text("Authentication and Authorization | user | Can view user")
        self.selenium.find_element(By.ID, "id_user_permissions_add").click()
        permissions_select.select_by_visible_text("Authentication and Authorization | user | Can change user")
        self.selenium.find_element(By.ID, "id_user_permissions_add").click()
        
        self.selenium.find_element(By.NAME, "_save").click()
        
        # Log out and log in with testuser
        self.selenium.find_element(By.XPATH, "//button[text()='Log out']").click()

        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        self.assertEqual( self.selenium.title , "Log in | Django site admin" )
        
        username_input = self.selenium.find_element(By.NAME,"username")
        username_input.send_keys('testuser')
        password_input = self.selenium.find_element(By.NAME,"password")
        password_input.send_keys('pirineus')
        self.selenium.find_element(By.XPATH,'//input[@value="Log in"]').click()
        
        self.assertEqual( self.selenium.title , "Site administration | Django site admin" )

        # Check if poll link is not available
        poll_link = self.selenium.find_elements(By.XPATH, "//a[@href='/admin/polls/']")
        assert len(poll_link) == 0
        
        # Check if it is possible to create/view users
        self.selenium.find_element(By.XPATH, "//a[@href='/admin/auth/user/']").click()
        self.assertEqual( self.selenium.title , "Select user to change | Django site admin" )
        self.selenium.find_element(By.XPATH, "//a[@href='/admin/auth/user/add/']").click()
        self.assertEqual( self.selenium.title , "Add user | Django site admin" )
