from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model
class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = "user_table"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Contact model should NOT inherit from AbstractUser
class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    aadhar_no = models.CharField(max_length=25, unique=True)
    phone_no = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contact_table"

    def __str__(self): 
        return f"{self.user.first_name} -> {self.user.last_name}"
    
