from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
import jinja2

router = APIRouter(prefix="/email_templates", tags=["email_templates"])

class TemplateRequest(BaseModel):
    template: str

@router.post("/preview")
async def preview_template(
    request: TemplateRequest,
    x_astra_test_key: str = Header(None)
):
    if x_astra_test_key != "Em41l_s3cr4t_t3mpl4t3s_b3_c4r3f4l":
        raise HTTPException(status_code=403, detail="Forbidden: Invalid or missing X-Astra-Test-Key")
    
    # VULNERABILITY: Server-Side Template Injection (SSTI)
    # The template is directly rendered from user input without sandboxing.
    environment = jinja2.Environment()
    try:
        template = environment.from_string(request.template)
        rendered = template.render()
        return {"rendered": rendered}
    except Exception as e:
        return {"error": str(e)}
