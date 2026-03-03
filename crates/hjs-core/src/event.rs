use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// HJS Event Types
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum Event {
    #[serde(rename = "lifecycle")]
    Lifecycle(LifecycleEvent),
    #[serde(rename = "verify")]
    Verify(VerifyEvent),
}

/// Lifecycle events: Judge, Delegate, Terminate
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LifecycleEvent {
    pub hjs: String,
    pub id: Uuid,
    pub actor: String,
    pub decision_hash: HashValue,
    pub authority_scope: String,
    pub valid: ValidityPeriod,
    pub state: State,
    pub prev_hash: Option<HashValue>,
    pub primitive: Primitive,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extensions: Option<serde_json::Value>,
    pub proof: Signature,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HashValue {
    pub hash: String,
    pub alg: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidityPeriod {
    pub from: u64,
    pub until: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum State {
    A, // Active
    D, // Delegated
    P, // Pending
    T, // Terminal
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Primitive {
    #[serde(rename = "type")]
    pub typ: PrimitiveType,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub payload: Option<serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum PrimitiveType {
    J, // Judge
    D, // Delegate
    T, // Terminate
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Signature {
    pub signature: String,
    pub alg: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub key_id: Option<String>,
}

/// Verify events: external attestation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerifyEvent {
    pub hjs: String,
    pub verify: VerifyPayload,
    pub proof: Signature,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerifyPayload {
    pub event_id: Uuid,
    pub method: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub attestation: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub verifier: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timestamp: Option<u64>,
}

impl LifecycleEvent {
    /// Create a new Judge event (genesis)
    pub fn judge(
        actor: impl Into<String>,
        decision_hash: HashValue,
        authority_scope: impl Into<String>,
        valid_from: u64,
        valid_until: u64,
    ) -> Self {
        Self {
            hjs: crate::HJS_VERSION.to_string(),
            id: Uuid::now_v7(),
            actor: actor.into(),
            decision_hash,
            authority_scope: authority_scope.into(),
            valid: ValidityPeriod {
                from: valid_from,
                until: valid_until,
            },
            state: State::A,
            prev_hash: None,
            primitive: Primitive {
                typ: PrimitiveType::J,
                payload: None,
            },
            extensions: None,
            proof: Signature {
                signature: String::new(),
                alg: "Ed25519".to_string(),
                key_id: None,
            },
        }
    }
}
