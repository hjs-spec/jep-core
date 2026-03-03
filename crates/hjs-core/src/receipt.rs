use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::event::HashValue;

/// HJS Receipt - portable, verifiable credential
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Receipt {
    pub hjs_receipt: String,
    pub version: String,
    pub event_id: Uuid,
    pub event_hash: HashValue,
    pub chain_proof: ChainProof,
    pub anchor_proof: AnchorProof,
    pub verification_mode: VerificationMode,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub platform_attestation: Option<PlatformAttestation>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extensions: Option<serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChainProof {
    #[serde(rename = "type")]
    pub typ: String, // "linear" or "merkle"
    pub anchor: HashValue,
    pub depth: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub merkle_path: Option<Vec<String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnchorProof {
    #[serde(rename = "type")]
    pub typ: String, // "memory", "tsp", "ots", "scitt", "platform"
    pub timestamp: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub uri: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum VerificationMode {
    Platform,
    Open,
    Dual,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlatformAttestation {
    pub issuer: String,
    pub issued_at: u64,
    pub signature: String,
    pub alg: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub key_id: Option<String>,
}
