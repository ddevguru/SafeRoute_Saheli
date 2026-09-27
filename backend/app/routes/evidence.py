"""
SafeRoute Saheli — Digital Evidence & Forensic Chain-of-Custody REST API (Phase 29)
Provides endpoints to generate signed forensic manifests and verify Merkle root integrity.
"""

from flask import Blueprint, request, jsonify, g
from backend.app.auth.jwt_handler import jwt_required
from backend.app.services.evidence_chain_service import EvidenceChainService

evidence_bp = Blueprint('evidence', __name__, url_prefix='/api/evidence')


@evidence_bp.route('/<string:incident_id>/chain-of-custody', methods=['GET'])
@jwt_required()
def get_chain_of_custody(incident_id: str):
    """
    Generate or retrieve certified digital chain-of-custody manifest
    for court admissibility, police forensics, and legal compliance.
    """
    try:
        manifest = EvidenceChainService.generate_chain_of_custody(incident_id)
        return jsonify({
            'success': True,
            'manifest': manifest
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as ex:
        return jsonify({'success': False, 'error': str(ex)}), 500


@evidence_bp.route('/verify-manifest', methods=['POST'])
def verify_manifest():
    """
    Public / forensic auditor verification endpoint:
    Validates Merkle root and cryptographic signature of a submitted manifest.
    """
    data = request.get_json() or {}
    manifest = data.get('manifest') or data
    result = EvidenceChainService.verify_manifest(manifest)
    return jsonify({
        'success': True,
        'verification': result
    }), (200 if result['is_valid'] else 400)
