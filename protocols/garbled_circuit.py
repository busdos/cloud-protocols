import mcl
from . import protocol_utils as ut


class GarbledCircuitUser:
    @staticmethod
    def decrypt_circuit_evaluation(
        encrypted_circuit_output: list[bytes],
        keys: list[bytes],
        input_bits: list[int]
    ) -> bytes:
        index = int(''.join(str(e) for e in input_bits), 2)
        ciphertext = encrypted_circuit_output[index]
        for key in keys:
            ciphertext = ut.xor_bytes(
                ciphertext,
                key
            )

        return ciphertext


class GarbledCircuitCloud:
    @staticmethod
    def _generate_labels(
        num_of_label_pairs: int
    ) -> list[tuple[bytes, bytes]]:
        """
        Labels are random byte string pairs, one corresponding
        to bit value 0 and the other to bit value 1.
        Depending on the bit provided by the client,
        either first or second label will be used
        for encryption.
        """
        labels = []

        for _ in range(num_of_label_pairs):
            labels.append((
                ut.compute_hash(mcl.Fr.rnd().getStr()),
                ut.compute_hash(mcl.Fr.rnd().getStr())
            ))

        return labels

    @staticmethod
    def evaluate_circuit_encrypt_output(circuit: list):
        """
        Circuit is just a list of all possible ouputs.
        Index 0 of the "circuit" corresponds to its output when provided input is an array of 0s,
        index 1 to input array [0 ... 0 1], index 2
        to input array [0 ... 1 0], etc.
        """
        assert ut.is_power_of_two(len(circuit)), f'{len(circuit)=} must be a power of 2'

        input_len = len(circuit).bit_length() - 1

        labels = GarbledCircuitCloud._generate_labels(
            input_len
        )

        ciphertexts = []
        for circ_val_idx, circ_val in enumerate(circuit):
            print(f'{circ_val=}')
            ciphertext = bytes(str(circ_val).zfill(ut._HASH_LENGTH), 'utf-8')
            print(f'{ciphertext=}')

            # Skip 0b prefix of the binary representation
            idx_bits = list(bin(circ_val_idx)[2:].zfill(input_len))
            print(f'{circ_val_idx=}')
            print(f'{input_len=}')
            print(f'{idx_bits=}')
            for bit_idx, bit in enumerate(idx_bits):
                ciphertext = ut.xor_bytes(
                    ciphertext,
                    labels[bit_idx][int(bit)]
                )

            print(f'{ciphertext=}')
            ciphertexts.append(ciphertext)

        return ciphertexts, labels
