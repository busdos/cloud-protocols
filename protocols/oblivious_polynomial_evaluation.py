"""
Oblivious polynomial evaluation protocol.
"""
from functools import reduce
from operator import add as add_func
from operator import mul as mul_func
from random import SystemRandom
from operator import itemgetter

from mcl import Fr


class OPEPolynomial():
    """
    Polynomial class for oblivious polynomial evaluation. Polynomial allows for setting of the coefficient of the smallest degree term as it serves as the value for which the Cloud will evaluate its internal polynomial.

    Polynomial's coefficients are stored in the
    following format (i.e. descending order of the
    degree):
        [a_n, a_(n-1), ..., a_1, a_0]
    where a_n is the coefficient of the term of
    the highest degree.
    """
    def __init__(self, deg: int, seed):
        self.coefficients = \
            OPEPolynomial._gen_coeffs(deg, seed)

    @staticmethod
    def _gen_coeffs(deg: int, seed) -> list[Fr]:
        return [
            Fr.setHashOf(f'{seed}{i}'.encode())
            for i in range(deg + 1)
        ]

    def regenerate_coefficients(self, deg: int, seed):
        self.coefficients = self._gen_coeffs(deg, seed)

    def set_val_at_zero(self, val):
        self.coefficients[-1] = val

    def deg(self):
        return len(self.coefficients) - 1

    def __len__(self):
        return len(self.coefficients)
    
    def __call__(self, x):
        """
        Compute the value of the polynomial at
        point x using the Horner's schema.
        """
        zero = Fr()
        zero.setInt(0)
        return reduce(lambda acc,
                      coef: acc * x + coef,
                      self.coefficients,
                      zero)

    def __getitem__(self, i):
        """
        Get the coefficient of the term of
        degree i. Since the coefficients are
        stored in descending order of the
        degree, the coefficient of the term
        of degree i is stored at index
        len(self) - 1 - i.
        """
        return self.coefficients[len(self) - 1 - i]
    
    def __setitem__(self, i, value):
        """
        Set the coefficient of the term of
        degree i. Since the coefficients are
        stored in descending order of the
        degree, the coefficient of the term
        of degree i is stored at index
        len(self) - 1 - i.
        """
        self.coefficients[len(self) - 1 - i] = value

    @staticmethod
    def lagrange_interpolation(x, phi):
        """
        Compute the Lagrange interpolation
        polynomial for the points in phi
        evaluated at point x.
        """
        def term(i):
            xi, yi = phi[i]
            numerator = [(x - phi[j][0])
                         for j in range(len(phi))
                         if j != i]
            denominator = [(xi - phi[j][0])
                           for j in range(len(phi))
                           if j != i]
            return yi * (reduce(mul_func, numerator) /
                         reduce(mul_func, denominator))

        return reduce(add_func,
                      [term(i) for i in range(len(phi))])


class OPECloud():
    @staticmethod
    def gen_main_polynomial(
            main_polynomial_degree: int,
            main_polynomial_seed: int,
    ) -> OPEPolynomial:
        return OPEPolynomial(
            main_polynomial_degree,
            main_polynomial_seed
        )

    @staticmethod
    def gen_mask_polynomial(
        mask_polynomial_degree: int,
        mask_polynomial_seed: int,
    ) -> OPEPolynomial:
        mask_polynomial = OPEPolynomial(
            mask_polynomial_degree,
            mask_polynomial_seed
        )

        zero = Fr()
        zero.setInt(0)
        mask_polynomial.set_val_at_zero(zero)

        return mask_polynomial


    @staticmethod
    def _compute_masked_poly(
        main_polynomial: OPEPolynomial,
        mask_polynomial: OPEPolynomial,
        x,
        y
    ):
        return mask_polynomial(x) + main_polynomial(y)

    @staticmethod
    def compute_masked_polynomial_values(
        main_polynomial: OPEPolynomial,
        mask_polynomial: OPEPolynomial,
        query_points: list[Fr]
    ):
        masked_p_values = []
        for x_val, y_val in query_points:
            masked_p_values.append(
                OPECloud._compute_masked_poly(
                    main_polynomial,
                    mask_polynomial,
                    x_val,
                    y_val
                )
            )

        return masked_p_values


class OPEClient():
    """
    Nomenclature:
        - Cloud's internal polynomial/main polynomial:
        polynomial of some known degree. Client wants
        to evaluate this polynomial at some point
        - Query polynomial: polynomial of degree equal
        to a value of a security parameter priorly
        agreed upon. The value of this polynomial at
        point 0 is the value at which the Cloud will
        evaluate its internal polynomial.
        - Result/response polynomial: polynomial of
        degree equal to the degree of the Cloud's
        internal polynomial. The value of this
        polynomial at point 0 is the result of the
        evaluation of the Cloud's internal polynomial
        at the value of the query polynomial at point 0.
        - Masking polynomial: polynomial of degree
        equal to (<degree of the main polynomial> *
        <degree of the query polynomial>).
        It is used to mask the main polynomial so that
        the Client is unable to interpolate the main
        polynomial (obviously until they query the Cloud
        enough times).
    """
    def __init__(self) -> None:
        self.rand = SystemRandom()
        # Array of indices indicating which points
        # of the last sent query are the ones
        # to use for interpolation of the result
        # polynomial
        self.query_point_indices = []
        self.query_x_values = []
    
    def gen_submerged_points_indices(
            self,
            size_of_interpolation_set: int,
            number_of_points: int
    ):
        """
        Generates a set of points which will be present on random
        postiions (hence the title "submerged") in the set of query
        points sent to the cloud.
        """
        self.query_point_indices = self.rand.sample(
            range(number_of_points),
            size_of_interpolation_set
        )

        return self.query_point_indices

    def gen_query_x_values(
            self,
            number_of_points: int
    ):
        self.query_x_values = [
            Fr.rnd()
            for _ in range(number_of_points)
        ]

        return self.query_x_values

    def produce_query_y_values(
            self,
            # Must already have its zero value set
            # to the value the Client wants to
            # evaluate the main polynomial at
            query_polynomial: OPEPolynomial
    ):
        assert self.query_point_indices != []
        assert self.query_x_values != []

        query_y_values = [
            query_polynomial(x) if i in self.query_point_indices else Fr.rnd()
            for i, x in enumerate(self.query_x_values)
        ]

        return query_y_values

    def eval_result_polynomial(
            self,
            cloud_response_points: list[Fr]
        ) -> Fr:
        """
        Interpolate the result polynomial using the points received from the Cloud and compute the value of the result polynomial at point 0.

        This value is equal to the value of the Cloud's internal polynomial at the value of the query polynomial at point 0 (i.e. the value for which 
        the Client wants to evaluate the main 
        polynomial).
        """
        iterpolation_x_values = list(
            itemgetter(*self.query_point_indices)
            (self.query_x_values)
        )

        interpolation_set = [
            (x, y)
            for x, y in zip(
                iterpolation_x_values, cloud_response_points
            )
        ]

        zero = Fr()
        zero.setInt(0)
        return OPEPolynomial.lagrange_interpolation(
            zero, interpolation_set
        )
