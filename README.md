# Post-Quantum Homomorphic Voting System

A secure electronic voting system that combines **Post-Quantum Cryptography (PQC)** with **Homomorphic Encryption** to ensure vote privacy, integrity, and resistance against future quantum-computing attacks.

This project demonstrates how modern cryptographic techniques can be integrated into digital voting systems to provide:

* Secure voter authentication
* Encrypted vote casting
* Privacy-preserving vote tallying
* Protection against quantum-era attacks
* Transparent and tamper-resistant election processes

---

#  Features

*  **Post-Quantum Cryptography**

  * Uses quantum-resistant cryptographic techniques for enhanced long-term security.

*  **Homomorphic Encryption**

  * Votes remain encrypted during tallying.
  * Results can be calculated without decrypting individual votes.

*  **Secure Voter Authentication**

  * Prevents unauthorized access and duplicate voting.

*  **Encrypted Vote Counting**

  * Maintains voter anonymity while ensuring accurate results.

*  **Privacy Preservation**

  * Individual votes are never exposed during the election process.

*  **Tamper Resistance**

  * Ensures election integrity and transparency.

---

#  Project Motivation

Traditional electronic voting systems face several security and privacy challenges, especially with the future emergence of quantum computers capable of breaking classical encryption methods.

This project aims to address those concerns by integrating:

* **Post-Quantum Cryptography** for future-proof security
* **Homomorphic Encryption** for confidential vote processing

The system demonstrates how secure and privacy-preserving digital elections can be implemented using advanced cryptographic methods.

---

#  System Architecture

The voting workflow follows these steps:

1. **Voter Registration**

   * Users register securely within the system.

2. **Authentication**

   * Verified voters gain access to the election portal.

3. **Vote Encryption**

   * Votes are encrypted using homomorphic encryption algorithms.

4. **Secure Vote Storage**

   * Encrypted votes are stored securely.

5. **Homomorphic Tallying**

   * Votes are counted directly in encrypted form.

6. **Final Decryption**

   * Only the final aggregated result is decrypted.

---

#  Security Concepts Used

## Post-Quantum Cryptography

Post-Quantum Cryptography refers to cryptographic algorithms designed to remain secure even against quantum computer attacks.

## Homomorphic Encryption

Homomorphic Encryption allows mathematical operations to be performed on encrypted data without decrypting it first.

This ensures:

* Ballot secrecy
* Secure tally computation
* End-to-end privacy

---

#  Technologies Used

* Python
* Cryptography Libraries
* Homomorphic Encryption Algorithms
* Post-Quantum Cryptographic Techniques
* Flask / Django 
* HTML/CSS/JavaScript (Frontend)

---

# ⚙️ Installation

## Clone the Repository

```bash
git clone https://github.com/AbihaEhtisham/PostQunatumHomomorphic_VotingSystem.git
cd PostQunatumHomomorphic_VotingSystem
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python app.py
```

---

# 📸 Screenshots

* Login Page
![Login Page](login.png)
* Voter Verification
![Voter Verification](voter_verification.png)
* Vote Receipt
![Vote Receipt](vote_receipt.png)
---

# ⭐ Acknowledgements

Inspired by modern research in:

* Homomorphic Encryption
* Post-Quantum Cryptography
* Secure Electronic Voting Systems

