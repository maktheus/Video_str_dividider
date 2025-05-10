import streamlit as st
import streamlit.components.v1 as components

def display_ad(ad_type="banner", slot_id="1234567890", client_id="ca-pub-1234567890123456", width=728, height=90):
    """
    Display Google AdSense ads in Streamlit.
    
    Args:
        ad_type (str): Type of ad ("banner", "display", "sidebar")
        slot_id (str): Your AdSense slot ID
        client_id (str): Your AdSense publisher ID (starts with ca-pub-)
        width (int): Width of the ad unit in pixels
        height (int): Height of the ad unit in pixels
    """
    # Create a placeholder colored div instead of actual ad during development
    ad_code = """
    <div style="width:{0}px; height:{1}px; background-color:#f0f0f0; border:1px dashed #ccc; 
         display:flex; align-items:center; justify-content:center; margin:auto; color:#666;">
        <div style="text-align:center;">
            <div style="font-weight:bold;">ANÚNCIO</div>
            <div style="font-size:12px;">{2} - {0}x{1}</div>
        </div>
    </div>
    """.format(width, height, ad_type.capitalize())
    
    # Display the ad using streamlit components
    components.html(ad_code, width=width, height=height)

def display_affiliate_ad(product_name="Amazon Echo", product_url="https://amzn.to/example", image_url=None, width=300, height=250):
    """
    Display affiliate product advertisement.
    
    Args:
        product_name (str): Name of the product
        product_url (str): Affiliate link to the product
        image_url (str): URL to product image
        width (int): Width of the ad
        height (int): Height of the ad
    """
    if image_url is None:
        # Placeholder image if none provided
        image_url = "https://via.placeholder.com/300x200?text=" + product_name.replace(" ", "+")
    
    ad_code = """
    <div style="width:{0}px; height:{1}px; border:1px solid #ddd; border-radius:5px; padding:10px; text-align:center; margin:auto;">
        <a href="{2}" target="_blank" style="text-decoration:none; color:inherit;">
            <img src="{3}" style="max-width:90%; max-height:60%; margin-bottom:10px;">
            <h3 style="margin:5px 0; color:#1e3a8a;">{4}</h3>
            <p style="margin:5px 0; color:#666;">Produto recomendado para quem trabalha com vídeos</p>
            <button style="background-color:#ff9900; color:white; border:none; padding:8px 15px; border-radius:4px; margin-top:10px; cursor:pointer;">
                Ver oferta
            </button>
        </a>
        <div style="font-size:9px; margin-top:5px; color:#999;">Anúncio</div>
    </div>
    """.format(width, height, product_url, image_url, product_name)
    
    components.html(ad_code, width=width, height=height)

def display_support_message():
    """Display a message asking for support with donation links."""
    st.markdown("""
    <div style="background-color:#f8f9fa; padding:15px; border-radius:5px; margin:10px 0;">
        <h4 style="color:#1e3a8a; margin-top:0;">💙 Apoie este projeto</h4>
        <p>
            Esta ferramenta é gratuita para uso. Se ela ajudou você, considere apoiar o seu desenvolvimento!
        </p>
        <a href="https://www.buymeacoffee.com/seuusername" target="_blank" style="display:inline-block; background-color:#FFDD00; color:#000000; padding:5px 15px; border-radius:5px; text-decoration:none; font-weight:bold; margin-right:10px;">
            ☕ Compre-me um café
        </a>
        <a href="https://github.com/seuusername/video-transcription-tool" target="_blank" style="display:inline-block; background-color:#24292e; color:#ffffff; padding:5px 15px; border-radius:5px; text-decoration:none; font-weight:bold;">
            ⭐ Star no GitHub
        </a>
    </div>
    """, unsafe_allow_html=True)

def show_video_tools_ads():
    """Display relevant video tools as affiliate ads."""
    st.markdown("### Ferramentas de Vídeo Recomendadas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_affiliate_ad(
            product_name="Microfone Profissional para Vídeos",
            product_url="https://amzn.to/example1",
            image_url="https://via.placeholder.com/300x200?text=Microfone",
            width=280,
            height=300
        )
        
    with col2:
        display_affiliate_ad(
            product_name="Software de Edição de Vídeo",
            product_url="https://amzn.to/example2",
            image_url="https://via.placeholder.com/300x200?text=Software",
            width=280,
            height=300
        )