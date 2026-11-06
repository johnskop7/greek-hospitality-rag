# Scope — greek-hospitality-rag

## What the app covers

Questions in Greek about **short-term rentals (βραχυχρόνια μίσθωση)** in Greece, answered only from official documents (ΑΑΔΕ, Υπουργείο Τουρισμού, gov.gr, ΦΕΚ).

**Out of scope:** hotels and other main tourist accommodation (ΜΗΤΕ, ειδικό σήμα λειτουργίας), long-term rentals, other countries, personal financial or legal advice. Questions about these should be **refused**.

## Topic rules

| ID | Topic | Rule: a question belongs here if it is about… |
|---|---|---|
| REG | Επιλεξιμότητα & εγγραφή | what you do **once**, before the first booking (or when you stop) |
| BKG | Δηλώσεις ανά κράτηση | what you do **again for every booking** |
| TAX | Φορολογία & τέλη | what you **pay** |
| SAF | Προδιαγραφές & ασφάλεια | what the **property itself** must have |
| RES | Περιορισμοί & έλεγχοι | **where/whether** you may rent at all, and **who checks** |

**Penalties** stay within their topic (e.g. the fine for not declaring a booking → BKG).

## Document set (proposed filenames)

| filename | Document | Publisher | Date |
|---|---|---|---|
| `aade_str_faq_2025.pdf` | Συχνές ερωτήσεις βραχυχρόνιας μίσθωσης (49 ερωτήσεις) | ΑΑΔΕ | 2025-09-23 |
| `aade_str_guide_2024.pdf` | Χρηστικός Οδηγός Βραχυχρόνιας Μίσθωσης Ακινήτων (μετά τον ν. 5073/2023) | ΑΑΔΕ | 2024-09 |
| `aade_takk_faq_2026.pdf` | Συχνές ερωτήσεις Τέλους Ανθεκτικότητας στην Κλιματική Κρίση | ΑΑΔΕ | 2026-01 |
| `mintour_str_specs_circular_2025.pdf` | Εγκύκλιος 19231/19.09.2025 — Προδιαγραφές ακινήτων βραχυχρόνιας μίσθωσης | Υπουργείο Τουρισμού | 2025-09-19 |
| `law_5170_2025.pdf` | Ν. 5170/2025 (ΦΕΚ Α' 6/20.01.2025), άρθρο 3 | ΦΕΚ | 2025-01-20 |
| `govgr_str_restrictions_2026.pdf` | Προσωρινοί περιορισμοί στις βραχυχρόνιες μισθώσεις (stegasi.gov.gr) | gov.gr | 2026-08-04 |
| `aade_pol1187_2017.pdf` | ΠΟΛ 1187/2017 — base decision for the Μητρώο & Δήλωση Βραχυχρόνιας Διαμονής | ΑΑΔΕ | 2017-11-23 |

## How to read the tables

- **Αναμενόμενο έγγραφο:** the `filename` that should contain the answer (retrieval ground truth for Milestone 3).
- **Status:** ✅ confirmed the document covers it · 🔍 likely, check by reading · ❌ not found in the document set → candidate for UNA or rewrite.
- **Σημειώσεις:** your decision: keep / rewrite / delete / move to UNA.

---

## REG — Επιλεξιμότητα & εγγραφή

| ID | Ερώτηση | Αναμενόμενο έγγραφο | Status | Σημειώσεις |
|---|---|---|---|---|
| REG-01 | Ποιος μπορεί να διαθέσει ακίνητο για βραχυχρόνια μίσθωση; Μόνο ο ιδιοκτήτης; | `aade_str_faq_2025.pdf` (Ερ. 28, 31, 34, 35) | ✅ | |
| REG-02 | Μπορώ να κάνω βραχυχρόνια μίσθωση σε ακίνητο που νοικιάζω (υπεκμίσθωση); | `aade_str_guide_2024.pdf` (§1.1), `aade_str_faq_2025.pdf` (Ερ. 35) | ✅ | |
| REG-03 | Πώς αποκτώ Αριθμό Μητρώου Ακινήτου (ΑΜΑ) και τι στοιχεία χρειάζομαι; | `aade_str_faq_2025.pdf` (Ερ. 30, 33, 35) | ✅ | |
| REG-04 | Από πόσα ακίνητα και πάνω πρέπει να κάνω έναρξη επιχειρηματικής δραστηριότητας; | `aade_str_guide_2024.pdf` (§3–4), `aade_str_faq_2025.pdf` (Ερ. 9, 11, 18) | ✅ | |
| REG-05 | Τι κάνω αν πουλήσω το ακίνητο ή σταματήσω να το νοικιάζω; | `aade_str_faq_2025.pdf` (Ερ. 40), `govgr_str_restrictions_2026.pdf` (μεταβίβαση) | ✅ | |
| REG-06 | Πρέπει να αναγράφω τον ΑΜΑ στην αγγελία της πλατφόρμας; | `aade_str_guide_2024.pdf` (§7) | ✅ | |

## BKG — Δηλώσεις ανά κράτηση

| ID | Ερώτηση | Αναμενόμενο έγγραφο | Status | Σημειώσεις |
|---|---|---|---|---|
| BKG-01 | Μέχρι πότε πρέπει να δηλώσω μια μίσθωση στην ΑΑΔΕ; | `aade_str_faq_2025.pdf` (Ερ. 42), `aade_str_guide_2024.pdf` | ✅ | ΑΑΔΕ often extends the deadline for specific months (e.g. Α.1227/2026) |
| BKG-02 | Τι στοιχεία του επισκέπτη και της κράτησης περιλαμβάνει η δήλωση; | `aade_pol1187_2017.pdf` | 🔍 | Not in the FAQ or guide |
| BKG-03 | Τι κάνω αν ακυρωθεί ή αλλάξει μια κράτηση που έχω ήδη δηλώσει; | `aade_str_faq_2025.pdf` (Ερ. 44), `aade_str_guide_2024.pdf` | ✅ | |
| BKG-04 | Πρέπει να δηλώνω και κρατήσεις χωρίς πλατφόρμα (απευθείας από τον πελάτη); | `aade_str_faq_2025.pdf` (Ερ. 3), `aade_str_guide_2024.pdf` (§2) | ✅ | |


## TAX — Φορολογία & τέλη

| ID | Ερώτηση | Αναμενόμενο έγγραφο | Status | Σημειώσεις |
|---|---|---|---|---|
| TAX-01 | Πώς φορολογείται το εισόδημα από βραχυχρόνια μίσθωση για φυσικό πρόσωπο; | `aade_str_faq_2025.pdf` (Ερ. 8, 13), `aade_str_guide_2024.pdf` (§3–4) | ✅ | |
| TAX-02 | Πότε επιβάλλεται ΦΠΑ στη βραχυχρόνια μίσθωση; | `aade_str_faq_2025.pdf` (Ερ. 10, 12, 22) | ✅ | |
| TAX-03 | Πόσο είναι το τέλος ανθεκτικότητας στην κλιματική κρίση ανά διανυκτέρευση και εποχή; | `fek_A1202_2024.pdf` | ✅ | |
| TAX-04 | Ποιος εισπράττει και ποιος αποδίδει το τέλος ανθεκτικότητας; | `aade_takk_faq_2026.pdf` (Ερ. 7, 9, 11), `aade_str_faq_2025.pdf` (Ερ. 23) | ✅ | |
| TAX-05 | Ποιο είναι το πρόστιμο αν δηλώσω εκπρόθεσμα το τέλος κλιματικής κρίσης; | `aade_str_faq_2025.pdf` (Ερ.60) | ✅ | |


## SAF — Προδιαγραφές & ασφάλεια

| ID | Ερώτηση | Αναμενόμενο έγγραφο | Status | Σημειώσεις |
|---|---|---|---|---|
| SAF-01 | Ποιος εξοπλισμός ασφαλείας είναι υποχρεωτικός (πυροσβεστήρας, ανιχνευτής καπνού, φαρμακείο); | `mintour_str_specs_circular_2025.pdf`, `law_5170_2025.pdf` | ✅ | |
| SAF-02 | Είναι υποχρεωτική η ασφάλιση αστικής ευθύνης; | `mintour_str_specs_circular_2025.pdf` | ✅ | |
| SAF-03 | Υπάρχουν ελάχιστες απαιτήσεις για φωτισμό ή αερισμό; | `mintour_str_specs_circular_2025.pdf` | ✅ | Light, ventilation and ceiling height ✅; |
| SAF-04 | Τι θα πρέπει να περιλαμβάνει το φαρμακείο πρώτων βοηθειών του ακινητού; | `mintour_str_specs_circular_2025.pdf` | ✅ | |
| SAF-05 | Από πότε ισχύουν οι νέες προδιαγραφές για τα ήδη εγγεγραμμένα ακίνητα; | `law_5170_2025.pdf` (άρθ. 3), `mintour_str_specs_circular_2025.pdf` | ✅ | |

## RES — Περιορισμοί & έλεγχοι

| ID | Ερώτηση | Αναμενόμενο έγγραφο | Status | Σημειώσεις |
|---|---|---|---|---|
| RES-01 | Μπορώ να εγγράψω νέο ακίνητο στο κέντρο της Αθήνας; | `govgr_str_restrictions_2026.pdf` | ✅ | Time-sensitive: ban runs to 31.12.2026, an extension is expected |
| RES-02 | Ισχύουν περιορισμοί για νησιά ή άλλες περιοχές; | `govgr_str_restrictions_2026.pdf` | ✅ | Only Athens (1st–3rd districts) + Thessaloniki (Α' Δημ. Κοινότητα) |
| RES-03 | Ποιος κάνει ελέγχους στα ακίνητα βραχυχρόνιας μίσθωσης; | `law_5170_2025.pdf` (άρθ. 3) | ✅ | Ministry of Tourism staff, joint teams with ΑΑΔΕ; €5,000 fines |
| RES-04 | Σε ποιες περιπτώσεις διαγράφεται ένα ακίνητο από το μητρώο; | `aade_str_faq_2025.pdf` (Ερ. 40), `govgr_str_restrictions_2026.pdf` | 🔍 | Partly covered (stopping management; transfer in restricted area) |

---

## UNA — Unanswerable (the app should refuse)

| ID | Ερώτηση | Τύπος | Σημειώσεις |
|---|---|---|---|
| UNA-01 | Πώς βγάζω σήμα ΜΗΤΕ για ξενοδοχείο; | εκτός θέματος | |
| UNA-02 | Ποιοι είναι οι κανόνες για Airbnb στην Ιταλία; | άλλη χώρα | |
| UNA-03 | Με συμφέρει να βγω από το Airbnb και να νοικιάσω μακροχρόνια; | προσωπική συμβουλή | |
| UNA-04 | Θα αυξηθεί το τέλος ανθεκτικότητας το 2028; | μέλλον / εικασία | |
| UNA-05 | Μπορεί ο κανονισμός της πολυκατοικίας να απαγορεύει τη βραχυχρόνια μίσθωση; | δεν καλύπτεται από τα έγγραφα | Civil-law issue, not in the set → UNA candidate |
| UNA-06 | Τι στοιχεία στέλνουν οι πλατφόρμες (π.χ. Airbnb) στην ΑΑΔΕ; | δεν καλύπτεται από τα έγγραφα | |
| UNA-07 | Τι γίνεται με την προμήθεια της πλατφόρμας: εκπίπτει ή φορολογείται; | δεν καλύπτεται από τα έγγραφα | |
| UNA-08 | Μπορεί να νοικιαστεί υπόγειος χώρος; | δεν καλύπτεται από τα έγγραφα | Basements not mentioned (only "χώροι κύριας χρήσης") → hard UNA |
