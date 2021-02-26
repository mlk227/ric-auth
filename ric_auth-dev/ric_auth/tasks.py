from celery.result import AsyncResult
from rest_framework import status, views
from rest_framework.response import Response


class GetTaskProgressView(views.APIView):
    """
    API endpoint that returns whether an Async job is finished, and 
    what to do with the job.
    """

    def get(self, request, *args, **kwargs):
        task_id = self.kwargs.get("task_id", None)
        if not task_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Please provide valid task id"})
        try:
            task = AsyncResult(task_id)

            data = {
                'state': task.state,
                'result': task.result
            }
            return Response(status=status.HTTP_200_OK, data=data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": str(e)})
