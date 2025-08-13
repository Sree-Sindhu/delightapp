import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st

class EmailHelper:
    """Email utility for Streamlit frontend to send emails via Gmail SMTP"""
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = "delightapi7@gmail.com"
        self.password = "kpsw tblj eggz hvtc"  # App password
    
    def send_order_confirmation(self, customer_email, customer_name, order_details):
        """Send order confirmation email to customer"""
        try:
            subject = "🍰 Your DelightAPI Order Confirmation"
            
            # Create HTML email content
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">🍰 DelightAPI</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">Your order is confirmed!</p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0;">
                        <h2 style="color: #667eea; margin-top: 0;">Hi {customer_name}! 👋</h2>
                        
                        <p>Thank you for your order! We're excited to prepare your delicious treats.</p>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                            <h3 style="margin-top: 0; color: #333;">📋 Order Details:</h3>
                            {order_details}
                        </div>
                        
                        <div style="background: #e8f4f8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 0;"><strong>🕐 Estimated Delivery:</strong> 2-3 hours</p>
                            <p style="margin: 5px 0 0 0;"><strong>📞 Need help?</strong> Contact us at delightapi7@gmail.com</p>
                        </div>
                        
                        <p style="margin-bottom: 0;">We'll notify you when your order is out for delivery!</p>
                        
                        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                            <p style="color: #666; margin: 0;">Thank you for choosing DelightAPI! 🧁</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(customer_email, subject, html_content, is_html=True)
            
        except Exception as e:
            st.error(f"Failed to send order confirmation: {str(e)}")
            return False
    
    def send_contact_notification(self, customer_email, customer_name, message):
        """Send notification when customer contacts support"""
        try:
            subject = f"📩 New Contact Message from {customer_name}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #667eea;">New Contact Message</h2>
                    <p><strong>From:</strong> {customer_name}</p>
                    <p><strong>Email:</strong> {customer_email}</p>
                    <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #667eea; margin: 15px 0;">
                        <p><strong>Message:</strong></p>
                        <p>{message}</p>
                    </div>
                    <p style="color: #666; font-size: 12px;">Sent via DelightAPI Contact Form</p>
                </div>
            </body>
            </html>
            """
            
            # Send to your business email
            return self._send_email(self.email, subject, html_content, is_html=True)
            
        except Exception as e:
            st.error(f"Failed to send contact notification: {str(e)}")
            return False
    
    def send_newsletter_signup(self, email, name=""):
        """Send welcome email for newsletter signup"""
        try:
            subject = "🌟 Welcome to DelightAPI Newsletter!"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333; padding: 30px; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">🍰 Welcome to DelightAPI!</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">You're now part of our sweet family! 🧁</p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0;">
                        <h2 style="color: #667eea; margin-top: 0;">Hi {name or 'Sweet Tooth'}! 👋</h2>
                        
                        <p>Thank you for subscribing to our newsletter! Get ready for:</p>
                        
                        <ul style="color: #555;">
                            <li>🎂 Exclusive cake recipes and baking tips</li>
                            <li>🎁 Special offers and discounts</li>
                            <li>🆕 New cake flavors and seasonal specials</li>
                            <li>📅 Early access to holiday collections</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 25px 0;">
                            <p style="background: #667eea; color: white; padding: 15px; border-radius: 8px; margin: 0; display: inline-block;">
                                🎉 Use code <strong>WELCOME10</strong> for 10% off your first order!
                            </p>
                        </div>
                        
                        <p>Stay tuned for delicious updates!</p>
                        
                        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                            <p style="color: #666; margin: 0;">Sweet regards,<br>The DelightAPI Team 🧁</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(email, subject, html_content, is_html=True)
            
        except Exception as e:
            st.error(f"Failed to send newsletter welcome: {str(e)}")
            return False
    
    def _send_email(self, to_email, subject, content, is_html=False):
        """Internal method to send email via Gmail SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add content
            if is_html:
                msg.attach(MIMEText(content, 'html'))
            else:
                msg.attach(MIMEText(content, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            
            text = msg.as_string()
            server.sendmail(self.email, to_email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Email sending error: {str(e)}")
            return False
    
    def test_email_connection(self):
        """Test if email configuration is working"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.quit()
            return True
        except Exception as e:
            st.error(f"Email connection test failed: {str(e)}")
            return False
