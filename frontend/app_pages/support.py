import streamlit as st
from typing import List, Dict
import sys
import os

# Add utils to path for email helper
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from email_helper import EmailHelper


def _bot_reply(user_text: str) -> str:
    """Very small rule-based bot for common queries."""
    t = (user_text or '').lower()
    if any(k in t for k in ['order', 'track', 'tracking']):
        return "You can track your order from Track page or Dashboard. If it’s out for delivery, you’ll also see ETA."
    if any(k in t for k in ['refund', 'cancel', 'cancellation']):
        return "Orders can be cancelled while status is Pending or Confirmed from Dashboard > your order. Refunds reflect in 5-7 business days."
    if any(k in t for k in ['address', 'change address', 'edit address']):
        return "Go to Profile > Addresses to add or edit delivery addresses before checkout."
    if any(k in t for k in ['login', 'password', 'reset']):
        return "Use the Login screen’s Reset Password option. If needed, contact support@delightapi.com."
    if any(k in t for k in ['custom', 'design', 'photo']):
        return "Use the Customize page to place custom cake orders at supporting stores."
    return "Thanks! I’ve noted your question. Our team will reply soon at support@delightapi.com."


def support_page():
    st.title("🛟 Help & Support")
    st.markdown("---")

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Live Chatbot")
        if 'support_chat' not in st.session_state:
            st.session_state.support_chat: List[Dict] = []
        chat = st.session_state.support_chat

        for entry in chat:
            role = entry.get('role')
            text = entry.get('content', entry.get('text', ''))
            if role == 'user':
                st.chat_message("user").markdown(text)
            else:
                st.chat_message("assistant").markdown(text)

        prompt = st.chat_input("Type your question…")
        if prompt:
            chat.append({'role': 'user', 'content': prompt})
            reply = _bot_reply(prompt)
            chat.append({'role': 'assistant', 'content': reply})
            st.session_state.support_chat = chat
            st.rerun()

    with c2:
        st.subheader("📞 Contact")
        st.write("📧 **Email:** delightapi7@gmail.com")
        st.write("📱 **Phone:** +91-9876543210")
        st.write("🕐 **Hours:** 9 AM - 9 PM (Daily)")
        
        with st.expander("📩 Send us a message", expanded=False):
            with st.form("contact_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Your Name *", placeholder="John Doe")
                with col2:
                    email = st.text_input("Your Email *", placeholder="john@example.com")
                
                subject = st.selectbox("Subject", [
                    "General Inquiry",
                    "Order Issue", 
                    "Delivery Problem",
                    "Refund Request",
                    "Custom Cake Order",
                    "Technical Support",
                    "Feedback/Suggestion"
                ])
                
                message = st.text_area("Your message *", 
                                     placeholder="Please describe your question or issue in detail...",
                                     height=100)
                
                submitted = st.form_submit_button("📤 Send Message")
                
                if submitted:
                    if not name or not email or not message:
                        st.error("Please fill in all required fields (marked with *)")
                    elif "@" not in email:
                        st.error("Please enter a valid email address")
                    else:
                        # Try to send email notification
                        try:
                            # Import here to avoid issues if module not available
                            import sys
                            import os
                            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
                            from email_helper import EmailHelper
                            
                            email_helper = EmailHelper()
                            
                            # Test connection first
                            if email_helper.test_email_connection():
                                # Send notification to business
                                full_message = f"Subject: {subject}\n\n{message}"
                                if email_helper.send_contact_notification(email, name, full_message):
                                    st.success("✅ Your message has been sent successfully! We'll get back to you within 24 hours.")
                                    
                                    # Optional: Send confirmation to customer
                                    confirmation_msg = f"""
                                    Thank you for contacting DelightAPI!
                                    
                                    We've received your message about: {subject}
                                    
                                    Our team will review your inquiry and respond within 24 hours.
                                    
                                    Best regards,
                                    DelightAPI Support Team
                                    """
                                    
                                    email_helper._send_email(email, "DelightAPI - Message Received", confirmation_msg)
                                else:
                                    st.error("Failed to send message. Please try again or contact us directly at delightapi7@gmail.com")
                            else:
                                st.error("Email service temporarily unavailable. Please contact us directly at delightapi7@gmail.com")
                                
                        except ImportError:
                            # Fallback if email helper not available
                            st.success("Your message has been noted. Our team will contact you at " + email)
                        except Exception as e:
                            st.error(f"Error sending message: {str(e)}")
                            st.info("Please contact us directly at delightapi7@gmail.com")
        
        # Email testing section (for development)
        with st.expander("🧪 Email Test (Dev)", expanded=False):
            st.write("**Test email functionality:**")
            test_email = st.text_input("Test email address", value="test@example.com")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Test Connection"):
                    try:
                        import sys
                        import os
                        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
                        from email_helper import EmailHelper
                        
                        email_helper = EmailHelper()
                        if email_helper.test_email_connection():
                            st.success("✅ Email connection successful!")
                        else:
                            st.error("❌ Email connection failed")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col2:
                if st.button("Test Welcome Email"):
                    try:
                        import sys
                        import os
                        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
                        from email_helper import EmailHelper
                        
                        email_helper = EmailHelper()
                        if email_helper.send_newsletter_signup(test_email, "Test User"):
                            st.success("✅ Welcome email sent!")
                        else:
                            st.error("❌ Failed to send email")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col3:
                if st.button("Test Order Email"):
                    try:
                        import sys
                        import os
                        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
                        from email_helper import EmailHelper
                        
                        email_helper = EmailHelper()
                        order_details = "<p>🍰 Chocolate Cake - ₹500</p><p>📍 Delivery: Test Address</p>"
                        if email_helper.send_order_confirmation(test_email, "Test Customer", order_details):
                            st.success("✅ Order confirmation sent!")
                        else:
                            st.error("❌ Failed to send email")
                    except Exception as e:
                        st.error(f"Error: {e}")

    st.markdown("---")
    st.subheader("FAQs")
    faqs = [
        ("How do I track my order?", "Go to the Track page or Dashboard and select your order to view status and ETA."),
        ("Can I cancel my order?", "Yes, while the status is Pending or Confirmed—open the order in Dashboard and tap Cancel."),
        ("How do I change my delivery address?", "Use Profile > Addresses to add/edit an address. Choose it at checkout."),
        ("Do you support custom cakes?", "Yes! Use the Customize page. Some stores show a ✅ Custom Cakes badge."),
        ("I forgot my password.", "Open Login and use Reset Password. If you’re stuck, mail support@delightapi.com."),
    ]
    for q, a in faqs:
        with st.expander(q):
            st.write(a)
