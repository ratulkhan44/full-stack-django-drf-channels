# Django Imports
from django.shortcuts import render
from django.db.models import Count

# Third Party imports
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, AuthenticationFailed

# In project Imports
from .models import Server
from .serializer import ServerSerializer
from .schema import server_list_docs

# Create your views here.

class ServerListViewset(viewsets.ViewSet):

    queryset = Server.objects.all()

    @server_list_docs
    def list(self, request):
        """
        Handles GET requests to retrieve a list of servers based on query parameters.

        Args:
        request (HttpRequest): The HTTP request object.

        Returns:
        Response: The HTTP response object containing the serialized server data.

        Raises:
        AuthenticationFailed: If the request requires authentication but the user is not authenticated.
        ValidationError: If there is an error validating the request or the requested server does not exist.

        Query Parameters:
        - `category (str)`: Filter the servers by category name.
        - `qty (str)`: Limit the number of servers returned.
        - `by_user (str)`: Filter the servers by the requesting user. Expected values: "true" or "false".
        - `by_serverid (str)`: Filter the servers by server ID.
        - `with_num_members (str)`: Annotate the servers with the number of members. Expected values: "true" or "false".

        Notes:
        - The authentication check is performed for query parameters 'by_user' and 'by_serverid'.
        - The 'category' parameter filters the queryset by the specified category name.
        - The 'with_num_members' parameter annotates the queryset with the number of members.
        - The 'by_user' parameter filters the queryset by the requesting user.
        - The 'qty' parameter limits the number of servers returned.
        - The 'by_serverid' parameter filters the queryset by server ID and checks its existence.

        Usage Example:
        GET /servers?category=game&qty=10&by_user=true&with_num_members=true

        """

        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"

        if category:
            # Filter queryset by category name
            self.queryset = self.queryset.filter(category__name=category)

        if with_num_members:
            # Annotate queryset with the number of members
            self.queryset = self.queryset.annotate(num_members=Count("member"))

        if by_user:
            # Filter queryset by the requesting user
            if by_user and request.user.is_authenticated:
                user_id = request.user.id
                self.queryset = self.queryset.filter(member=user_id)
            else:
                raise AuthenticationFailed()


        if by_serverid:
            if not request.user.is_authenticated:
                raise AuthenticationFailed()
            try:
                # Filter queryset by server id and check existence
                self.queryset = self.queryset.filter(id=by_serverid)
                print("00000000000",self.queryset)
                if not self.queryset.exists():
                    raise ValidationError(detail=f"Server with id {by_serverid} not found")
            except Exception as e:
                print("aasas",e.args[0])
                raise ValidationError(detail="Server value error")
            
        if qty:
            # Limit the queryset by the specified quantity
            self.queryset = self.queryset[:int(qty)]
            print("------------",self.queryset)

        # Serialize queryset with optional context and return response
        serializer = ServerSerializer(self.queryset, many=True, context={"num_members": with_num_members})
        return Response(serializer.data)
