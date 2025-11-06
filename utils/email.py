import resend
import base64
from datetime import datetime

def crear_template_email(nombre_usuario, tipo_reporte, metricas_resumen):
    """Crea template HTML profesional para el email"""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 30px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px;
                text-align: center;
                color: white;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 30px;
            }}
            .greeting {{
                font-size: 18px;
                color: #333;
                margin-bottom: 20px;
            }}
            .info-box {{
                background-color: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .metric {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #e0e0e0;
            }}
            .metric:last-child {{
                border-bottom: none;
            }}
            .metric-label {{
                font-weight: 600;
                color: #555;
            }}
            .metric-value {{
                color: #667eea;
                font-weight: bold;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💰 Simulador Financiero</h1>
                <p>Universidad Nacional de Trujillo</p>
            </div>
            
            <div class="content">
                <p class="greeting">Hola <strong>{nombre_usuario}</strong>,</p>
                
                <p>Tu reporte de <strong>{tipo_reporte}</strong> ha sido generado exitosamente.</p>
                
                <div class="info-box">
                    <h3 style="margin-top: 0; color: #667eea;">📊 Resumen del Reporte</h3>
                    {metricas_resumen}
                </div>
                
                <p>Encuentra adjunto el reporte completo en formato PDF con todos los detalles y análisis.</p>
                
                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Este reporte fue generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}
                </p>
            </div>
            
            <div class="footer">
                <p><strong>Simulador Financiero - Finanzas Corporativas</strong></p>
                <p>Grupo 6 - Universidad Nacional de Trujillo</p>
                <p style="margin-top: 10px;">© 2025 Todos los derechos reservados</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template


def enviar_email_con_pdf_resend(email_destino, nombre_usuario, pdf_buffer, 
                                 tipo_reporte, metricas_dict):
    """
    Envía email usando Resend con PDF adjunto y template personalizado
    """
    try:
        # Crear HTML con las métricas
        metricas_html = ""
        for label, valor in metricas_dict.items():
            metricas_html += f"""
            <div class="metric">
                <span class="metric-label">{label}</span>
                <span class="metric-value">{valor}</span>
            </div>
            """
        
        # Generar template completo
        html_content = crear_template_email(nombre_usuario, tipo_reporte, metricas_html)
        
        # Preparar PDF para adjuntar
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.read()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Nombre del archivo
        filename = f"reporte_{tipo_reporte.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Enviar email
        params = {
            "from": "Simulador Financiero <onboarding@resend.dev>",
            "to": [email_destino],
            "subject": f"📊 Tu Reporte de {tipo_reporte}",
            "html": html_content,
            "attachments": [{
                "filename": filename,
                "content": pdf_base64
            }]
        }
        
        email = resend.Emails.send(params)
        return True, email
        
    except Exception as e:
        return False, str(e)