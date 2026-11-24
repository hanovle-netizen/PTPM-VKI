import unittest

from src.delivery_service import calculate_delivery_cost

ERROR = (-1, "0000-00-00")
START = "2026-09-03"


class TestDeliveryValidation(unittest.TestCase):
    def test_weight_below_minimum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(0.09, 100, "обычный"), ERROR)

    def test_weight_above_maximum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(50.1, 100, "обычный"), ERROR)

    def test_minimum_weight_is_accepted(self):
        self.assertNotEqual(calculate_delivery_cost(0.1, 100, "обычный"), ERROR)

    def test_maximum_weight_is_accepted(self):
        self.assertNotEqual(calculate_delivery_cost(50.0, 100, "обычный"), ERROR)

    def test_distance_below_minimum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(1, 0, "обычный"), ERROR)

    def test_distance_above_maximum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(1, 5001, "обычный"), ERROR)

    def test_boundary_distances_are_accepted(self):
        for distance in (1, 5000):
            with self.subTest(distance=distance):
                self.assertNotEqual(calculate_delivery_cost(1, distance, "обычный"), ERROR)

    def test_unknown_package_type_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "скоропортящийся"), ERROR)

    def test_negative_weight_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(-5, 100, "обычный"), ERROR)


class TestDeliveryCost(unittest.TestCase):
    def test_basic_cost_for_light_regular_package(self):
        # 200 + 100 * 5
        self.assertEqual(calculate_delivery_cost(1, 100, "обычный")[0], 700)

    def test_weight_exactly_five_kg_has_no_surcharge(self):
        self.assertEqual(calculate_delivery_cost(5.0, 100, "обычный")[0], 700)

    def test_medium_weight_has_surcharge_20_percent(self):
        self.assertEqual(calculate_delivery_cost(10, 100, "обычный")[0], 840)

    def test_weight_just_below_twenty_has_surcharge_20_percent(self):
        self.assertEqual(calculate_delivery_cost(19.9, 100, "обычный")[0], 840)

    def test_weight_twenty_kg_and_more_has_surcharge_50_percent(self):
        self.assertEqual(calculate_delivery_cost(20, 100, "обычный")[0], 1050)

    def test_fragile_package_adds_300(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "хрупкий")[0], 1000)

    def test_dangerous_package_adds_1000(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "опасный")[0], 1700)

    def test_express_delivery_is_more_expensive_than_regular(self):
        regular = calculate_delivery_cost(1, 1000, "обычный")[0]
        express = calculate_delivery_cost(1, 1000, "обычный", True)[0]
        self.assertGreater(
            express, regular,
            msg=f"Экспресс-доставка должна стоить дороже обычной: экспресс {express} руб., обычная {regular} руб.",
        )

    def test_cost_grows_with_distance(self):
        near = calculate_delivery_cost(1, 100, "обычный")[0]
        far = calculate_delivery_cost(1, 2000, "обычный")[0]
        self.assertGreater(far, near)

    def test_cost_is_integer(self):
        self.assertIsInstance(calculate_delivery_cost(7.3, 123, "хрупкий")[0], int)


class TestDeliveryDate(unittest.TestCase):
    def test_short_distance_takes_one_day(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "обычный")[1], "2026-09-04")

    def test_one_day_per_500_km(self):
        self.assertEqual(calculate_delivery_cost(1, 2000, "обычный")[1], "2026-09-07")

    def test_express_is_faster_than_regular(self):
        regular = calculate_delivery_cost(1, 2000, "обычный")[1]
        express = calculate_delivery_cost(1, 2000, "обычный", True)[1]
        self.assertLess(express, regular)

    def test_express_short_distance_is_not_same_day(self):
        date = calculate_delivery_cost(1, 100, "обычный", True)[1]
        self.assertGreater(
            date, START,
            msg=f"Экспресс не может прийти в день отправки: отправка {START}, доставка {date}",
        )

    def test_delivery_date_is_after_shipping_date(self):
        self.assertGreater(calculate_delivery_cost(1, 1, "обычный")[1], START)


if __name__ == "__main__":
    unittest.main()
