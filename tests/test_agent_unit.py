import json
import subprocess

import pytest
from PIL import Image
from pydantic import ValidationError

from aseprite_mcp.core import config
from aseprite_mcp.core.contract import AssetContract, validate_frames
from aseprite_mcp.core.errors import LuaToolError, WorkspaceError
from aseprite_mcp.core.runner import _parse_result


def fixture():
    spec = AssetContract.model_validate({'name':'robot', 'cell':{'width':8,'height':8},
        'rows':[{'direction':'down','frames':2}], 'palette':['#ff0000'],
        'anchor':{'max_foot_drift':0.0, 'max_center_drift':0.0}})
    frames = [Image.new('RGBA',(8,8)) for _ in range(2)]
    for im in frames:
        im.paste((255,0,0,255),(2,2,6,7))
    return spec, {'tags':[{'name':'down','from':1,'to':2}]}, frames


def test_agent_unit_good_contract():
    spec, info, frames = fixture()
    assert validate_frames(info,frames,spec)['passed']


@pytest.mark.parametrize('kind,rule',[('alpha','binary_alpha'),('palette','palette_membership'),('empty','empty_frame'),('drift','anchor_foot_drift'),('count','frame_count'),('tag','tag_layout'),('geometry','cell_geometry')])
def test_agent_unit_detects_bad_asset(kind,rule):
    spec, info, frames = fixture()
    if kind == 'alpha': frames[0].putpixel((2,2),(255,0,0,100))
    if kind == 'palette': frames[0].putpixel((2,2),(0,0,255,255))
    if kind == 'empty': frames[0] = Image.new('RGBA',(8,8))
    if kind == 'drift': frames[0].putpixel((3,7),(255,0,0,255))
    if kind == 'count': frames.pop()
    if kind == 'tag': info['tags'] = []
    if kind == 'geometry': frames[0] = Image.new('RGBA',(9,8))
    report = validate_frames(info,frames,spec)
    assert not report['passed']
    assert rule in [f['rule'] for f in report['failures']]


def test_agent_unit_unknown_contract_field():
    spec,_,_ = fixture()
    with pytest.raises(ValidationError):
        AssetContract.model_validate({**spec.model_dump(), 'anchors':{}})


@pytest.mark.parametrize('path',['../escape.aseprite','x/../../escape','NUL.png','safe.png:stream','{layer}.png','bad. /x','C:relative.png','x\n.lua'])
def test_agent_unit_unsafe_paths(path,tmp_path,monkeypatch):
    monkeypatch.setenv('ASEPRITE_MCP_WORKSPACE',str(tmp_path))
    monkeypatch.setenv('ASEPRITE_MCP_ALLOW_ABSOLUTE','1')
    monkeypatch.setenv('ASEPRITE_AGENT_ALLOWED_ROOTS','[]')
    with pytest.raises(WorkspaceError): config.resolve(path)


def test_agent_unit_optin_still_confined(tmp_path,monkeypatch):
    monkeypatch.setenv('ASEPRITE_MCP_WORKSPACE',str(tmp_path/'ws'))
    monkeypatch.setenv('ASEPRITE_MCP_ALLOW_ABSOLUTE','1')
    monkeypatch.setenv('ASEPRITE_AGENT_ALLOWED_ROOTS','[]')
    with pytest.raises(WorkspaceError): config.resolve(str(tmp_path/'outside.png'))


def test_agent_unit_allowed_absolute(tmp_path,monkeypatch):
    monkeypatch.setenv('ASEPRITE_MCP_WORKSPACE',str(tmp_path/'ws'))
    monkeypatch.setenv('ASEPRITE_MCP_ALLOW_ABSOLUTE','1')
    monkeypatch.setenv('ASEPRITE_AGENT_ALLOWED_ROOTS',json.dumps([str(tmp_path/'other')]))
    assert config.resolve(str(tmp_path/'other'/'good.png')) == tmp_path/'other'/'good.png'


def test_agent_unit_nonzero_with_result_is_failure():
    with pytest.raises(LuaToolError):
        _parse_result(subprocess.CompletedProcess([],1,'@@ASEMCP@@{"ok":true}','crash'))



def test_agent_unit_export_cannot_replace_master(tmp_path, monkeypatch):
    from aseprite_mcp.core.errors import ExportError
    from aseprite_mcp.core.paths import ensure_output_path
    monkeypatch.setenv('ASEPRITE_MCP_WORKSPACE', str(tmp_path))
    with pytest.raises(ExportError, match='editable master'):
        ensure_output_path('hero.aseprite', overwrite=True, error_type=ExportError)


def test_agent_unit_curated_tools():
    import asyncio

    from aseprite_mcp.agent_server import DISABLED, configure, mcp
    configure()
    names = {t.name for t in asyncio.run(mcp.list_tools())}
    assert not names.intersection(DISABLED)
    assert {'ase_export_phaser', 'ase_validate_asset_contract', 'ase_apply_and_preview'}.issubset(names)
