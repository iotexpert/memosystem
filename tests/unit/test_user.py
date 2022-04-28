from docmgr.models.User import User

"""
    username = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean,default=False)
    readAll = db.Column(db.Boolean,default=False)
    pagesize = db.Column(db.Integer, nullable=False, default = 20)
    _subscriptions = db.Column(db.String(128))

https://www.martinfowler.com/bliki/GivenWhenThen.html
Feature: User trades stocks
  Scenario: User requests a sell before close of trading
    Given I have 100 shares of MSFT stock
       And I have 150 shares of APPL stock
       And the time is before close of trading

    When I ask to sell 20 shares of MSFT stock
     
     Then I should have 80 shares of MSFT stock
      And I should have 150 shares of APPL stock
      And a sell order for 20 shares of MSFT stock should have been executed
      
      Given: The initial conditions of the test
      When: What is occuring that needs to be tested
      Then: What is the expected response
"""
     
def dont_test_new_user():
    """Given 
    """
    user = User(username='test12',email="test1@test.local",password="123",admin=False,readAll=False,pagesize=10)
    print(f'{user}')
#    db.session.add(user)
#    db.session.commit()

    assert user.admin == False
    assert user.pagesize == 10