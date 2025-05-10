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
    # Cria um div de placeholder estilizado em vez do AdSense real
    # Quando você tiver sua conta AdSense aprovada, pode substituir isso pelo código real
    ad_code = """
    <div style="width:{}px; height:{}px; background-color:#f7f9fc; border-radius:8px; 
         box-shadow:0 2px 10px rgba(0,0,0,0.05); overflow:hidden; margin:auto; color:#5a6778;
         display:flex; align-items:center; justify-content:center; margin:15px auto; transition:all 0.3s ease;">
        <div style="text-align:center; padding:10px;">
            <div style="font-weight:500; color:#4287f5; margin-bottom:5px;">Conteúdo patrocinado</div>
            <div style="font-size:11px; opacity:0.8;">{}</div>
            <div style="margin-top:10px; font-size:10px; color:#8a98a8;">Anúncios ajudam a manter esta ferramenta gratuita</div>
        </div>
    </div>
    """.format(width, height, ad_type.capitalize())
    
    # Quando tiver sua conta AdSense aprovada, descomente o código abaixo
    # e insira seus IDs reais do AdSense:
    """
    ad_code = '<div style="width:{}px; height:{}px; overflow:hidden; margin:auto;">'.format(width, height)
    ad_code += '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={}">'.format(client_id)
    ad_code += '</script>'
    ad_code += '<!-- {} Ad -->'.format(ad_type.capitalize())
    ad_code += '<ins class="adsbygoogle" style="display:block" data-ad-client="{}" data-ad-slot="{}"'.format(client_id, slot_id)
    ad_code += ' data-ad-format="auto" data-full-width-responsive="true"></ins>'
    ad_code += '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'
    ad_code += '</div>'
    """
    
    # Display the ad using streamlit components
    components.html(ad_code, width=width, height=height)

def display_affiliate_ad(product_name="Amazon Echo", product_url="https://amzn.to/example", image_url=None, width=300, height=320, description=None):
    """
    Display affiliate product advertisement.
    
    Args:
        product_name (str): Name of the product
        product_url (str): Affiliate link to the product
        image_url (str): URL to product image
        width (int): Width of the ad
        height (int): Height of the ad
        description (str): Custom product description
    """
    if image_url is None:
        # Placeholder image if none provided
        image_url = "https://via.placeholder.com/300x200?text=" + product_name.replace(" ", "+")
        
    if description is None:
        description = "Ferramenta essencial para criadores de conteúdo de vídeo"
    
    ad_code = """
    <div style="width:{}px; height:{}px; background-color:white; border-radius:12px; 
         box-shadow:0 4px 15px rgba(0,0,0,0.08); overflow:hidden; margin:15px auto; transition:transform 0.3s ease;">
        <a href="{}" target="_blank" style="text-decoration:none; color:inherit; display:block;">
            <div style="height:55%; overflow:hidden; position:relative; background:#f0f2f5;">
                <img src="{}" style="width:100%; height:100%; object-fit:cover; transition:transform 0.5s ease;">
            </div>
            <div style="padding:15px;">
                <h3 style="margin:0 0 8px 0; color:#1e3a8a; font-size:16px; font-weight:600; line-height:1.3;">{}</h3>
                <p style="margin:0 0 12px 0; color:#4a5568; font-size:13px; line-height:1.4;">{}</p>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <button style="background-color:#4287f5; color:white; border:none; padding:8px 15px; border-radius:6px; 
                           font-weight:500; cursor:pointer; transition:background 0.3s ease;">
                        Conferir
                    </button>
                    <div style="font-size:10px; color:#a0aec0; text-align:right;">Produto<br>recomendado</div>
                </div>
            </div>
        </a>
    </div>
    """.format(width, height, product_url, image_url, product_name, description)
    
    components.html(ad_code, width=width, height=height)

def display_support_message():
    """Display a message asking for support with donation links."""
    # Importar configurações aqui para evitar importação circular
    from ad_config import SUPPORT_LINKS
    
    st.markdown(f"""
    <div style="background-color:#f0f6ff; padding:20px; border-radius:12px; margin:15px 0; 
         box-shadow:0 2px 12px rgba(66, 135, 245, 0.1); border-left:4px solid #4287f5;">
        <h3 style="color:#1e3a8a; margin-top:0; font-size:18px; font-weight:600;">💙 Transforme seus vídeos em conteúdo impactante</h3>
        <p style="color:#4a5568; margin:8px 0 15px; line-height:1.5; font-size:14px;">
            Esta ferramenta é <strong>totalmente gratuita</strong> e ajuda criadores como você todos os dias. 
            Se ela economizou seu tempo ou melhorou seu trabalho, considere apoiar o projeto para que possamos 
            continuar evoluindo com novos recursos!
        </p>
        <div style="display:flex; flex-wrap:wrap; gap:12px;">
            <a href="{SUPPORT_LINKS['coffee']}" target="_blank" 
               style="display:inline-flex; align-items:center; gap:8px; background-color:#FFDD00; color:#000000; 
                      padding:10px 16px; border-radius:8px; text-decoration:none; font-weight:600; 
                      transition:transform 0.2s ease, box-shadow 0.2s ease; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                ☕ Apoiar com um café
            </a>
            <a href="{SUPPORT_LINKS['github']}" target="_blank" 
               style="display:inline-flex; align-items:center; gap:8px; background-color:#2b3137; color:#ffffff; 
                      padding:10px 16px; border-radius:8px; text-decoration:none; font-weight:600; 
                      transition:transform 0.2s ease, box-shadow 0.2s ease; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                ⭐ Estrela no GitHub
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_video_tools_ads():
    """Display relevant video tools as affiliate ads."""
    # Importar configurações aqui para evitar importação circular
    from ad_config import AFFILIATE_LINKS, AFFILIATE_IMAGES
    
    st.markdown("""
    <div style="margin-top:30px; margin-bottom:10px;">
        <h2 style="color:#1e3a8a; font-size:24px; font-weight:600; margin-bottom:5px;">
            ✨ Eleve seu conteúdo ao próximo nível
        </h2>
        <p style="color:#4a5568; font-size:15px; margin-top:0;">
            Ferramentas profissionais recomendadas por especialistas em produção de vídeo
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_affiliate_ad(
            product_name="Microfone Profissional BlueSky",
            product_url=AFFILIATE_LINKS["microphone"],
            image_url=AFFILIATE_IMAGES["microphone"],
            width=300,
            height=320,
            description="Áudio cristalino para suas gravações. Ideal para narrações, podcasts e entrevistas com redução de ruído ambiente."
        )
        
    with col2:
        display_affiliate_ad(
            product_name="VideoMaster Pro - Editor Profissional",
            product_url=AFFILIATE_LINKS["software"],
            image_url=AFFILIATE_IMAGES["software"],
            width=300,
            height=320,
            description="Editor completo com recursos de IA para legendas automáticas, efeitos visuais e transições profissionais."
        )
        
    # Linha opcional com mais produtos
    if "camera" in AFFILIATE_LINKS and "course" in AFFILIATE_LINKS:
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        
        with col3:
            display_affiliate_ad(
                product_name="Câmera Ultra HD ZoomPro",
                product_url=AFFILIATE_LINKS["camera"],
                image_url=AFFILIATE_IMAGES["camera"],
                width=300,
                height=320,
                description="Capture vídeos em 4K com estabilização avançada. Perfeita para YouTubers e criadores de conteúdo digital."
            )
            
        with col4:
            display_affiliate_ad(
                product_name="Curso Master em Produção de Vídeo",
                product_url=AFFILIATE_LINKS["course"],
                image_url=AFFILIATE_IMAGES["course"],
                width=300,
                height=320,
                description="Aprenda técnicas profissionais de edição, iluminação e captação de áudio com especialistas da indústria."
            )