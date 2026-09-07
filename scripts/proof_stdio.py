"""Sanitized proof; all authoring and validation go through the MCP stdio client.
Run: uv run python scripts/proof_stdio.py --output /absolute/new-proof-directory
ASEPRITE_PATH must identify your own Aseprite installation.
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def proof(output):
    output.mkdir(parents=True,exist_ok=False)
    env = {**os.environ,'ASEPRITE_MCP_WORKSPACE':str(output), 'ASEPRITE_MCP_ALLOW_ABSOLUTE':'0', 'ASEPRITE_AGENT_ALLOWED_ROOTS':'[]'}
    params = StdioServerParameters(command=sys.executable,args=['-m','aseprite_mcp.agent_server'],env=env)
    transcript=[]
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            tools = await session.list_tools()
            async def call(name,args):
                result=await session.call_tool(name,args)
                if result.isError: raise RuntimeError(f'{name}: {result}')
                values=[]
                for item in result.content:
                    if item.type=='text':
                        try: values.append(json.loads(item.text))
                        except ValueError: values.append(item.text)
                    elif item.type=='image':
                        import base64
                        (output/f'preview-{len(transcript)}.png').write_bytes(base64.b64decode(item.data))
                transcript.append({'tool':name,'result':values})
                return values[0] if values else None
            health=await call('health_check',{})
            assert health['ok'], health
            await call('create_sprite',{'filename':'robot.aseprite','width':16,'height':16})
            ops=[{'op':'rename_layer','args':{'layer':'Layer 1','new_name':'body'}}]
            for f in range(2,17): ops.append({'op':'add_frame','args':{'duration_ms':100}})
            for row,direction in enumerate(['down','left','right','up']):
                ops.append({'op':'add_tag','args':{'name':direction,'from':row*4+1,'to':row*4+4}})
                for phase in range(4):
                    f=row*4+phase+1
                    for x,y,w,h,color in [(4,3,8,9,'#315c88'),(5,4,6,4,'#8bd5ed'),(4,12,3,2,'#223344'),(9,12,3,2,'#223344'),(5+(phase%2)*4,5,2,2,'#223344')]:
                        ops.append({'op':'fill_rectangle','args':{'frame':f,'layer':'body','x':x,'y':y,'width':w,'height':h,'color':color}})
                    # Direction marker and phase pixel make all sixteen frames distinguishable.
                    ops.append({'op':'set_pixel','args':{'frame':f,'layer':'body','x':5+row,'y':9,'color':'#8bd5ed'}})
                    ops.append({'op':'set_pixel','args':{'frame':f,'layer':'body','x':5+phase,'y':10,'color':'#223344'}})
            await call('ase_apply_and_preview',{'filename':'robot.aseprite','operations':ops})
            await call('set_palette',{'filename':'robot.aseprite','colors':['#315c88','#8bd5ed','#223344']})
            contract={'name':'robot','cell':{'width':16,'height':16},'rows':[{'direction':d,'frames':4} for d in ['down','left','right','up']], 'palette':['#315c88','#8bd5ed','#223344'],'anchor':{'max_foot_drift':0.0,'max_center_drift':0.0}}
            qa=await call('ase_validate_asset_contract',{'filename':'robot.aseprite','contract':contract})
            assert qa['passed'],qa
            assert len({f['rgba_sha256'] for f in qa['frames']})==16
            await call('ase_preview_animation',{'filename':'robot.aseprite'})
            await call('save_sprite_as',{'filename':'robot.aseprite','new_filename':'reopened.aseprite'})
            copied=await call('ase_validate_asset_contract',{'filename':'reopened.aseprite','contract':contract})
            assert copied['frames']==qa['frames']
            exported=await call('ase_export_phaser',{'filename':'robot.aseprite','output_directory':'phaser','contract':contract})
            assert exported['ok'] and exported['qa']['roundtrip']['passed']
            await call('export_gif',{'filename':'robot.aseprite','output':'robot.gif','scale':4})
            # Failure must leave the master byte-identical.
            before=(output/'robot.aseprite').read_bytes()
            failed=await session.call_tool('ase_apply_and_preview',{'filename':'robot.aseprite','operations':[{'op':'set_pixel','args':{'x':0,'y':0,'color':'red'}},{'op':'remove_layer','args':{'layer':'does-not-exist'}}]})
            assert failed.isError
            assert (output/'robot.aseprite').read_bytes()==before
            overwrite=await session.call_tool('ase_export_phaser',{'filename':'robot.aseprite','output_directory':'phaser','contract':contract})
            assert overwrite.isError
            escape=await session.call_tool('create_sprite',{'filename':'../escape.aseprite','width':8,'height':8})
            assert escape.isError
            # Actual invalid fixture must fail QA and not publish an export directory.
            await call('save_sprite_as',{'filename':'robot.aseprite','new_filename':'broken.aseprite'})
            await call('ase_apply_and_preview',{'filename':'broken.aseprite','operations':[{'op':'set_pixel','args':{'x':0,'y':15,'color':'#ff00ff80'}}]})
            broken=await call('ase_export_phaser',{'filename':'broken.aseprite','output_directory':'rejected','contract':contract})
            assert not broken['ok'] and not (output/'rejected').exists()
    report={'passed':True,'transport':'MCP stdio','tools_available':len(tools.tools),'frames':16,'distinct_frames':16,'roundtrip':True,'batch_rollback':True,'overwrite_rejected':True,'escape_rejected':True,'broken_contract_rejected':True,'transcript':transcript}
    (output/'proof.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='transcript'},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    asyncio.run(proof(args.output.resolve()))
