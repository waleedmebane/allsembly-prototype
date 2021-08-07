from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='UserId', max_length=255)
    password = forms.CharField(label='Password', max_length=1024)


class ArgueForm(forms.Form):
    target_position_text = forms.CharField(widget=forms.HiddenInput)
    target_position = forms.IntegerField(widget=forms.HiddenInput)
    pro_or_con = forms.ChoiceField(choices=[('Pro', 'support'),('Con', 'oppose')],
                                   widget=forms.RadioSelect,
                                   initial='Pro')
    first_premise = forms.CharField(label='Premises:', widget=forms.Textarea)
    bid_on_first_premise = forms.FloatField(label='Bid:', initial=51.0,
                                              max_value=99.999999999,
                                              min_value=0.000000001)
    inf_premise = forms.CharField(label='Inferential premise (optional):',
                                  widget=forms.Textarea,
                                  required=False)
    bid_on_inf_premise = forms.FloatField(label='Bid:', initial=99.0,
                                            max_value=99.999999999,
                                            min_value=0.000000001)


class ProposeForm(forms.Form):
    position_text = forms.CharField(label='Initial position text:', widget=forms.Textarea)