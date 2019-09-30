def dilate(original_x, original_y, origin_point, dilate_factor):
    dilated_x = float(origin_point.x() + dilate_factor * (original_x - origin_point.x()))
    dilated_y = float(origin_point.y() + dilate_factor * (original_y - origin_point.y()))
    return dilated_x, dilated_y


def undilate(dilated_x, dilated_y, origin_point, dilate_factor):
    original_x = float(origin_point.x() + (dilated_x - origin_point.x()) / dilate_factor)
    original_y = float(origin_point.y() + (dilated_y - origin_point.y()) / dilate_factor)
    return original_x, original_y


def scale_factor_hint(outer_rect, inner_rect, ratio):
    return (outer_rect.width() / ratio) / inner_rect.width()
