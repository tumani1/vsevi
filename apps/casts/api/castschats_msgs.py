# coding: utf-8

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.casts.models import CastsChatsMsgs
from apps.casts.forms import CastsChatGetForm
from apps.casts.api.serializers import vbCastChatMsg


################################################################################
transform_map = {
    'id_low': lambda query, arg: query.filter(id__gte=arg),
    'id_high': lambda query, arg: query.filter(id__lte=arg),
    'limit': lambda query, arg: query[:arg]
}


class CastsChatsMsgsView(APIView):
    """
    Cast info
    """

    def get(self, request, cast_id, *args, **kwargs):
        try:
            form = CastsChatGetForm(data=request.GET)
            if form.is_valid():
                query = CastsChatsMsgs.objects.filter(cast=cast_id)
                for field in form.cleaned_data:
                    if form.cleaned_data[field]:
                        query = transform_map[field](query, form.cleaned_data[field])

                return Response(vbCastChatMsg(query, many=True).data, status=status.HTTP_200_OK)

            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        except CastsChatsMsgs.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
