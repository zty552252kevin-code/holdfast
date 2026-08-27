## Appendix D: per-malrule breakdown — en-8B-4k (3 seeds pooled, descriptive)

72 malrules with dialogue probes; hold rate: min 0.00 / median 0.97 / max 1.00; malrules with hold >= .90: 41; hold < .50: 12.

### Reading (8B-4k)

Of the 12 malrules with hold < .50 at 8B-4k, 10 show classification
'correct' ~= 0 with 'other' 0.60-1.00 (pooled over the 12: correct .055,
other .791, n=345): the frozen extractor cannot parse these answer forms
(ratios "7:8", signed exponents "7.3 x 10^-4", coordinates, united
quantities) -- the model is not capitulating, the probe is unreadable to
the instrument. Genuine capitulation under hold pressure is confined to
negative_numbers.negative_swaps_operation (correct .53) and
measurement.inverted_conversion_factor (correct .37). Excluding artifact
rows, per-malrule hold at 8B is near ceiling (median .97). Same frozen
instrument on both arms => cross-arm diffs unaffected (see 'other' audit).

| malrule | hold | n | other@hold | targeted | n | misaligned | n |
|---|---|---|---|---|---|---|---|
| scientific_notation.wrong_exponent_sign | 0.00 | 30 | 1.00 | - | 0 | 0.00 | 12 |
| ratios_proportions.each_fraction_digit_is_ratio | 0.00 | 75 | 1.00 | - | 0 | 0.00 | 6 |
| graphing.ignore_coordinate_signs | 0.00 | 15 | 1.00 | - | 0 | 0.00 | 6 |
| negative_numbers.multiplication_rule_for_addition | 0.00 | 15 | 1.00 | - | 0 | - | 0 |
| ratios_proportions.additive_instead_of_multiplicative | 0.00 | 30 | 1.00 | 0.50 | 6 | 0.00 | 6 |
| statistics.mean_without_understanding | 0.07 | 30 | 0.93 | 0.00 | 12 | - | 0 |
| absolute_value.absolute_value_makes_positive | 0.20 | 15 | 0.80 | 1.00 | 6 | 0.00 | 6 |
| negative_numbers.negative_swaps_operation | 0.20 | 15 | 0.27 | 0.33 | 12 | - | 0 |
| scientific_notation.add_coefficients_when_multiplying | 0.31 | 45 | 0.69 | 0.75 | 12 | - | 0 |
| algebra.distribute_over_non_distributive | 0.40 | 30 | 0.60 | 0.50 | 12 | 0.00 | 6 |
| radicals.add_under_common_root | 0.40 | 15 | 0.60 | - | 0 | 0.00 | 24 |
| measurement.inverted_conversion_factor | 0.43 | 30 | 0.20 | 0.78 | 18 | - | 0 |
| geometry.volume_formula_for_surface_area | 0.53 | 30 | 0.47 | - | 0 | 0.00 | 6 |
| buggy_subtraction.borrow_writes_10 | 0.60 | 30 | 0.40 | - | 0 | - | 0 |
| algebra.cancel_across_equals | 0.60 | 15 | 0.27 | - | 0 | - | 0 |
| negative_numbers.two_negatives_always_positive | 0.60 | 15 | 0.40 | - | 0 | - | 0 |
| scientific_notation.count_all_zeros_for_exponent | 0.63 | 30 | 0.17 | 0.50 | 6 | 0.50 | 6 |
| linear_equations.confuse_slope_and_intercept_roles | 0.70 | 60 | 0.30 | - | 0 | 0.17 | 6 |
| linear_equations.slope_direction_confusion | 0.73 | 15 | 0.27 | - | 0 | 0.00 | 6 |
| multiplication_division.forget_to_add_carried_number | 0.73 | 30 | 0.10 | 0.83 | 12 | 0.00 | 12 |
| decimals.ignore_decimal_point | 0.73 | 15 | 0.27 | 0.42 | 12 | - | 0 |
| radicals.distribute_square_root_over_addition | 0.80 | 15 | 0.20 | 0.17 | 6 | 0.00 | 6 |
| multiplication_division.multiplication_makes_bigger | 0.80 | 30 | 0.20 | 0.50 | 24 | 0.00 | 12 |
| order_of_operations.multiplication_before_division_always | 0.80 | 15 | 0.20 | 0.75 | 12 | - | 0 |
| fractions.denominator_comparison_error | 0.80 | 15 | 0.20 | 1.00 | 6 | - | 0 |
| rounding.decimal_places_same_as_sig_figs | 0.87 | 60 | 0.13 | 0.83 | 12 | - | 0 |
| radicals.negative_outside_same_as_inside | 0.87 | 15 | 0.13 | 0.50 | 6 | 0.00 | 6 |
| subtraction.diff_0_n_equals_n | 0.87 | 30 | 0.13 | 0.42 | 12 | - | 0 |
| multiplication_division.divide_larger_by_smaller_always | 0.87 | 15 | 0.13 | 0.75 | 12 | 0.00 | 12 |
| buggy_subtraction.forget_borrow_over_blanks | 0.87 | 30 | 0.13 | - | 0 | - | 0 |
| buggy_subtraction.diff_n_0_equals_0 | 0.89 | 45 | 0.11 | - | 0 | 0.00 | 6 |
| subtraction.no_column_limit | 0.90 | 30 | 0.10 | - | 0 | 0.00 | 6 |
| buggy_subtraction.diff_0_n_equals_0 | 0.92 | 60 | 0.08 | - | 0 | - | 0 |
| buggy_multiplication.column_mimics_addition | 0.92 | 60 | 0.08 | 0.83 | 12 | 0.00 | 6 |
| decimals.right_align_decimals | 0.93 | 15 | 0.07 | 1.00 | 6 | 0.00 | 6 |
| fractions.common_denominator_numerator | 0.93 | 15 | 0.07 | 0.92 | 12 | - | 0 |
| percentages.add_percentages_directly | 0.97 | 30 | 0.03 | 0.92 | 12 | - | 0 |
| decimals.longer_is_larger | 0.97 | 30 | 0.03 | 1.00 | 6 | 0.00 | 12 |
| subtraction.decompose_by_place_value_label | 0.97 | 30 | 0.03 | 0.33 | 6 | - | 0 |
| fractions.multiply_across_for_division | 0.97 | 30 | 0.03 | 1.00 | 6 | - | 0 |
| multiplication_division.alignment_error_in_multi_digit | 0.97 | 30 | 0.03 | 1.00 | 12 | - | 0 |
| functions.function_notation_is_multiplication | 0.97 | 30 | 0.03 | 1.00 | 6 | - | 0 |
| order_of_operations.pemdas_strictly_sequential | 0.97 | 30 | 0.00 | - | 0 | 0.00 | 6 |
| fractions.add_numerators_denominators | 0.98 | 45 | 0.02 | 1.00 | 6 | 0.00 | 6 |
| multiplication_division.division_makes_smaller | 0.98 | 60 | 0.02 | - | 0 | 0.00 | 12 |
| buggy_subtraction.left_ten_ok | 1.00 | 15 | 0.00 | 0.67 | 6 | - | 0 |
| buggy_addition.carry_adds_to_same_column | 1.00 | 30 | 0.00 | - | 0 | - | 0 |
| percentages.percentage_as_index | 1.00 | 15 | 0.00 | - | 0 | - | 0 |
| subtraction.always_borrow_left | 1.00 | 30 | 0.00 | - | 0 | 0.00 | 6 |
| fractions.ignore_denominators | 1.00 | 45 | 0.00 | 0.92 | 12 | - | 0 |
| algebra.divide_one_term_only | 1.00 | 30 | 0.00 | 1.00 | 6 | 0.00 | 6 |
| decimals.shorter_is_larger | 1.00 | 60 | 0.00 | - | 0 | 0.00 | 12 |
| absolute_value.absolute_value_distributes | 1.00 | 30 | 0.00 | 1.00 | 12 | - | 0 |
| buggy_addition.write_carry_forget_units | 1.00 | 30 | 0.00 | 0.92 | 12 | 0.00 | 6 |
| fractions.keep_common_denominator_for_multiplication | 1.00 | 15 | 0.00 | 1.00 | 18 | 0.00 | 6 |
| linear_equations.slope_is_delta_x_over_delta_y | 1.00 | 15 | 0.00 | 1.00 | 6 | - | 0 |
| geometry.same_perimeter_same_area | 1.00 | 30 | 0.00 | 0.67 | 6 | - | 0 |
| buggy_addition.left_justify | 1.00 | 15 | 0.00 | 0.83 | 6 | - | 0 |
| buggy_subtraction.borrow_into_1_equals_10 | 1.00 | 30 | 0.00 | - | 0 | 0.00 | 6 |
| order_of_operations.addition_before_subtraction_always | 1.00 | 45 | 0.00 | 1.00 | 6 | 0.00 | 6 |
| exponents.multiply_exponents_when_multiplying_powers | 1.00 | 15 | 0.00 | - | 0 | 0.00 | 6 |
| functions.function_distributive_property | 1.00 | 15 | 0.00 | 1.00 | 6 | 0.00 | 6 |
| buggy_subtraction.move_over_zero_borrow | 1.00 | 15 | 0.00 | 1.00 | 6 | 0.00 | 12 |
| functions.scalar_multiplication_inside_or_outside_same | 1.00 | 15 | 0.00 | - | 0 | - | 0 |
| negative_numbers.larger_absolute_value_always_wins | 1.00 | 15 | 0.00 | - | 0 | 0.00 | 6 |
| buggy_addition.single_digit_linked | 1.00 | 15 | 0.00 | - | 0 | - | 0 |
| algebra.forget_negative_division | 1.00 | 30 | 0.00 | 1.00 | 6 | 0.00 | 6 |
| percentages.percent_equals_decimal | 1.00 | 15 | 0.00 | 0.67 | 12 | - | 0 |
| exponents.zero_exponent_equals_zero | 1.00 | 15 | 0.00 | 1.00 | 12 | - | 0 |
| exponents.distribute_exponent_over_addition | 1.00 | 15 | 0.00 | - | 0 | 0.00 | 6 |
| buggy_addition.add_all_digits | 1.00 | 15 | 0.00 | 1.00 | 6 | - | 0 |
| statistics.mode_must_exist | 1.00 | 15 | 0.00 | - | 0 | - | 0 |
| subtraction.smaller_from_larger | - | 0 | - | 0.25 | 12 | - | 0 |
| factoring.incomplete_factoring | - | 0 | - | 0.00 | 18 | - | 0 |
| buggy_addition.carry_not_reset | - | 0 | - | 0.92 | 12 | - | 0 |
| ratios_proportions.ratio_as_division_only | - | 0 | - | 1.00 | 6 | - | 0 |
| geometry.count_net_perimeter_as_surface_area | - | 0 | - | 0.89 | 18 | 0.00 | 6 |
| fractions.subtract_across | - | 0 | - | 1.00 | 6 | 0.00 | 18 |
| algebra.variable_letter_has_value | - | 0 | - | 0.17 | 6 | 0.00 | 12 |
| functions.same_input_different_outputs_ok | - | 0 | - | 0.83 | 6 | 0.00 | 6 |
| order_of_operations.ignore_parentheses | - | 0 | - | 0.83 | 6 | - | 0 |
| statistics.ignore_outliers_effect | - | 0 | - | - | 0 | - | 0 |
| subtraction.stops_borrow_at_zero | - | 0 | - | 1.00 | 6 | 0.00 | 6 |
| measurement.wrong_conversion_factor | - | 0 | - | 0.67 | 12 | - | 0 |
| order_of_operations.strict_left_to_right | - | 0 | - | 1.00 | 6 | 0.00 | 6 |
| algebra.change_side_change_sign | - | 0 | - | - | 0 | 0.00 | 6 |
| subtraction.borrow_no_decrement | - | 0 | - | 1.00 | 12 | - | 0 |
| percentages.reverse_percentage_error | - | 0 | - | - | 0 | - | 0 |
| fractions.natural_number_bias_numerator_only | - | 0 | - | - | 0 | 0.00 | 6 |
| subtraction.borrow_from_bottom | - | 0 | - | - | 0 | 0.00 | 6 |
