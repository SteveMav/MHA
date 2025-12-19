from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from .models import Annonce

@receiver(post_save, sender=Annonce)
def send_announcement_email(sender, instance, created, **kwargs):
    """
    Sends an email to members when a new announcement is created.
    """
    if created:
        subject = f"Nouvelle Annonce : {instance.titre}"
        from_email = settings.DEFAULT_FROM_EMAIL
        
        # Determine recipients
        if instance.cible == 'tous':
            recipients = User.objects.filter(is_active=True).exclude(email='')
        elif instance.cible == 'individuel':
            recipients = instance.membres_cibles.filter(is_active=True).exclude(email='')
        else:
            recipients = User.objects.filter(is_active=True).exclude(email='')

        recipient_list = [user.email for user in recipients]

        if not recipient_list:
            return

        # Prepare context
        domain = '127.0.0.1:8000' 
        
        context = {
            'annonce': instance,
            'domain': domain,
            'logo_cid': 'logo_mha',
            'image_cid': 'announcement_img' if instance.image else None
        }

        html_content = render_to_string('announcements/email/news_notification.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject,    
            text_content,
            from_email,
            bcc=recipient_list
        )
        msg.attach_alternative(html_content, "text/html")
        msg.mixed_subtype = 'related' # Necessary for inline images

        # Attach Logo
        try:
            from django.contrib.staticfiles.finders import find
            from email.mime.image import MIMEImage
            import os

            logo_path = find('images/mha_logo.jpeg')
            if logo_path:
                with open(logo_path, 'rb') as f:
                    logo_data = f.read()
                logo = MIMEImage(logo_data)
                logo.add_header('Content-ID', '<logo_mha>')
                msg.attach(logo)
        except Exception as e:
            print(f"Error attaching logo: {e}")

        # Attach Announcement Image
        if instance.image:
            try:
                # Open the image file from storage
                with instance.image.open('rb') as f:
                    img_data = f.read()
                image = MIMEImage(img_data)
                image.add_header('Content-ID', '<announcement_img>')
                msg.attach(image)
            except Exception as e:
                print(f"Error attaching announcement image: {e}")

        try:
            msg.send()
        except Exception as e:
            # Handle error silently or log it so it doesn't crash the request
            print(f"Error sending email: {e}")
            # In production, use logging.error(f"Error sending email: {e}")
