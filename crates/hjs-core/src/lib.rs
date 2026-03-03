//! HJS: A Judgment Event Protocol
//! 
//! Implementation of [draft-wang-hjs-judgment-event](https://datatracker.ietf.org/doc/draft-wang-hjs-judgment-event/)
//! 
//! ## Core Concepts
//! - **Judge**: Establish accountability for a decision
//! - **Delegate**: Transfer responsibility to another actor  
//! - **Terminate**: Conclude accountability
//! - **Verify**: Independent attestation
//! - **Receipt**: Portable, verifiable credential

pub mod event;
pub mod receipt;
pub mod crypto;

pub use event::{Event, LifecycleEvent, VerifyEvent, Primitive, PrimitiveType, State};
pub use receipt::{Receipt, VerificationMode, ChainProof, AnchorProof};

/// Protocol version
pub const HJS_VERSION: &str = "1.0";
