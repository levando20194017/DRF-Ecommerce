def get_client_ip(request):
    # Thử lấy IP từ header HTTP_X_FORWARDED_FOR
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Trường hợp có nhiều proxy, IP thực sẽ là cái đầu tiên trong chuỗi
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        # Nếu không qua proxy, lấy IP trực tiếp từ REMOTE_ADDR
        ip = request.META.get('REMOTE_ADDR')
    return ip
